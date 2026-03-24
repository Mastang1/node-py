# Demo 02 开发说明：静态组成、动态流程与导出模型

本文档说明 `demo_02` 中**仪器 API 发现 → 节点（NODE）→ NODE FLOW → Python 导出**的完整链路，区分**静态代码结构**与**运行时/构建时动态行为**，并与当前「仅导出函数体」的导出策略对齐。

---

## 1. 静态组成 vs 动态流程

| 维度 | 静态（随仓库发布） | 动态（运行期或扫描期变化） |
|------|-------------------|---------------------------|
| 节点类 | `nodes.py` 中 `WorkflowNode` 子类（开始、变量、注释、静态仪器封装等） | `api_dynamic_nodes` 为每个 API 方法**生成**的类，类对象在首次扫描后进入内存 |
| 资源树 | `ResourceTreeWidget` + `node_registry.grouped_templates()` 的布局与交互 | 树中**条目集合**随 `ensure_instrument_api_registered()` 更新 |
| 画布上的图 | JSON 会话可保存/加载 | 节点实例、连线、属性值随用户操作变 |
| 导出文本 | 导出算法在 `workflow_exporter.py` 中固定 | 导出结果内容随当前图结构变化 |

---

## 2. 从 `Instruments_pythonic/` 发现仪器 API 的原理

### 2.1 扫描入口

- 模块：`demo_02/api_dynamic_nodes.py` 中 `discover_api_method_metas()`。
- 默认扫描包：`demo_02.Instruments_pythonic`（即目录 `demo_02/Instruments_pythonic/` 下的子模块，如 `signal_generator.py`、`general.py` 等）。
- 使用 `pkgutil.iter_modules` 枚举子模块，`importlib.import_module` 加载每个 `.py`，再用 `inspect.getmembers(..., inspect.isclass)` / `inspect.isfunction` 遍历**本模块内定义的类与方法**。

### 2.2 如何从 docstring 变成「API 元数据」

- 符合条件的**实例方法**若带有约定格式的文档字符串，会经 `_parse_method_meta(...)` 解析为不可变数据类 `ApiMethodMeta`：模块名、类名、方法名、中英文节点名、分类、参数/返回值/流程出口等。
- 未按约定写 docstring 的方法**不会**出现在元数据列表中，因而**不会**变成节点。

### 2.3 缓存

- 对 `Instruments_pythonic` 目录下参与扫描的 `.py` 做指纹（文件名 + mtime 等），与 `generated/api_discovery_cache.json` 中保存的指纹比对。
- 指纹一致则**直接读 JSON 恢复 `ApiMethodMeta` 列表**，避免重复解析；否则全量扫描并写回缓存。

### 2.4 与左侧资源树的关系

- `node_registry.ensure_instrument_api_registered(graph)` 调用 `discover_api_method_metas()`，为每个 meta `get_or_create_dynamic_class(meta)` 得到具体 Python 类，并向 `NodeGraph` **注册**尚未注册过的 `type_`。
- `ResourceTreeWidget.rebuild()` 通过 `grouped_templates()` 读取**当前已注册的全部节点类型**（静态 + 动态），因此仪器相关节点**不是写死在 UI 里的固定列表**，而是扫描结果 + 注册表的反映。
- 应用启动时在主窗口初始化末尾也会执行一次发现与 `rebuild()`，保证无需手动点「加载仪器 API」也能看到动态类（仍保留菜单动作用于刷新/二次注册场景）。

---

## 3. 仪器 API 如何形成 NODE（图节点类型）

### 3.1 动态类生成

- `get_or_create_dynamic_class(meta)`（`api_dynamic_nodes.py`）为每个 `ApiMethodMeta` 构建一个 **`DynamicApiMethodNode` 的子类**（或复用已缓存类），挂上 `API_META`、`FIELD_SPECS`、数据端口/流程端口等。
- `type_` 使用稳定标识（如 `demo02.api.<registry_key>`），保证会话 JSON 与注册表一致。

### 3.2 与静态节点的统一

- 静态节点在 `nodes.py` 中定义，由 `graph_factory.build_configured_node_graph` → `register_all_nodes` 注册。
- 动态节点在 `ensure_instrument_api_registered` 中增量 `graph.register_nodes(new_types)`。
- 二者均继承 `WorkflowNode`，共享端口约束配置 `configure_graph_port_constraints`、校验 `WorkflowValidator`、运行时 `WorkflowRuntime`、导出 `emit_python`。

### 3.3 运行时执行（简述）

- GUI/子进程运行时：`DynamicApiMethodNode.execute` 内 `importlib.import_module(meta.module_name)`，取类实例，调用真实方法；控制类节点（分支/循环等）走 `_execute_control_node`。
- 调试线程里仍用 `emit_python` + `ExportContext` 生成逐节点片段；**文件导出**走另一套「线性脚本」逻辑（见下节）。

---

## 4. NODE FLOW 导出为 Python 的原理（当前：线性调用 + `run_flow()`）

### 4.1 设计意图

- 导出文本应**直接可读**：按图上 **Start 出发的 visit 顺序**，一行一类调用，例如 `delay(1.0)`、`comment("…")`、`set_variable(variables, …)`，仪器类则 `SimSignalGeneratorIvi()` / `sg.configure_waveform(...)` 等。
- 顶层 **`return` 在模块中非法**，因此用**薄包装** `def run_flow():` 包住上述语句；你可把函数体剪贴到自己的测试函数里，或整文件 `exec` 后调用 `run_flow()`。
- 局部状态：`variables`、`sessions`、`_last` 均在 `run_flow()` 内；与 GUI 的 `FlowContext` 概念对应，但**无** `NODE_DISPATCH` / `while` 多态调度表。

### 4.2 映射范围

- 已映射：注释、延时、`general` 的 `set_variable` / `return_value` / `raise_error`、常用常量与读写变量、简单数学/比较/布尔、静态仪器会话 open/use/close、多数动态 API 方法（控制流类节点导出为 `# TODO` 提示手写）。
- 未映射或复杂数据依赖：导出为 `# TODO` 行，需手写或后续补规则。

### 4.3 图分析

- `analyze_flow_graph` 的 `ordered_nodes`（DFS visit 顺序）即导出顺序；校验仍用该顺序做会话绑定检查。

### 4.4 测试与冒烟

- `demo_02/tests/test_linear_flow_export.py`：`pytest` 校验导出字符串形态并 `exec` + `run_flow()`。
- `demo_02.py --headless-smoke-test`：导出示例流程后对整文件 `exec` 并调用 `run_flow()` 一次。

---

## 5. 相关源文件索引

| 主题 | 路径 |
|------|------|
| API 扫描与缓存 | `demo_02/api_dynamic_nodes.py` |
| 动态节点类 | `demo_02/api_dynamic_nodes.py`（`DynamicApiMethodNode`） |
| 注册与资源树数据 | `demo_02/node_registry.py` |
| 仪器 Pythonic 桩/实现 | `demo_02/Instruments_pythonic/*.py` |
| 图分析与运行 | `demo_02/workflow_runtime.py` |
| 导出 | `demo_02/workflow_exporter.py` |
| 校验 | `demo_02/workflow_validator.py` |
| 架构分层说明 | `demo_02/docs/ARCHITECTURE.md` |
| 产品说明与设计迭代 | `design_2.md` |

---

*文档版本：与「线性导出 + `run_flow()`」行为同步。*

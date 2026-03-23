# `demo_02` 最新实现 Prompt（第一阶段落地版）

## 1. 任务目标
保留现有的 `@NodeGraphQt_notes/demo_01.py` 不改动，在 `@NodeGraphQt_notes/` 下新建 `demo_02/` 目录，并在其中实现一个新的、可运行、可验证闭环的 `NodeGraphQt` 仪器图形化编程 demo。

本次 `demo_02` 的目标不是一次性做完所有高级控制流，而是先做出一个“第一阶段可闭环落地”的系统，要求：

- 能启动完整 GUI；
- 能自动加载节点资源树；
- 能把仪器动作节点拖拽到 NodeGraphQt 画布；
- 能编辑节点参数；
- 能保存 / 加载 node flow；
- 能导出可直接运行的 Python 脚本；
- 能在 GUI 内执行 node flow；
- 能展示运行日志、校验信息和导出源码；
- 能按 `@NodeGraphQt_notes/prompts_note.md` 完成代码构建闭环：实现后必须本地运行、发现问题自行修复、直到通过验证再交付。

---

## 2. 本次实现必须遵循的硬约束

### 2.1 闭环要求
开发完成后必须执行本地闭环验证，至少包括：

1. 启动 GUI 主程序；
2. 自动或程序化创建一条示例 flow；
3. 执行 flow，确认日志正常输出；
4. 保存 flow 为 JSON；
5. 重新加载该 JSON；
6. 导出 Python 脚本；
7. 运行导出的 Python 脚本；
8. 如果有任何报错或行为不符合需求，必须自行修复并重复验证。

### 2.2 兼容与依赖要求
- 优先使用现有本地 `NodeGraphQt` 源码。
- 不要引入大型新依赖；右侧可折叠面板优先用 Qt 自带控件或自定义轻量控件实现。
- 所有图标使用本地 SVG 文件。
- 所有可见控件和动作都要有 tooltip。
- 默认语言为简体中文，支持切换到 English。
- 默认主题为暗色，支持切换到浅色。

### 2.3 范围约束
本次实现按“第一阶段落地版”处理，不追求完整通用流程语言。

明确约束如下：

- 本阶段执行模型采用“无环 DAG + 顺序执行”为主。
- 本阶段不支持真正的回边循环，不实现可视化 `for/while` 真循环执行。
- 本阶段不把“整个仪器类”拖成一个大节点，而是采用“会话节点 + 动作节点”设计。
- 本阶段资源树展示的是“节点模板资源树”，不是 Python 文件树，也不是源码浏览器。
- 本阶段导出目标固定为独立 `.py` 文件，文件中必须包含可直接运行的 `run_flow(context=None)`。

---

## 3. 本次实现中，已经拍板的设计决策

### 3.1 节点粒度决策
节点粒度采用以下模式：

1. 仪器会话节点
- 用于创建 / 打开 / 初始化某个仪器会话。
- 例如：`Open Signal Generator Session`

2. 仪器动作节点
- 用于对已有仪器会话执行某个动作。
- 例如：`Configure Waveform`、`Output Enable`、`Read Serial`

3. 通用流程节点
- 用于构成基础流程。
- 本阶段必须至少实现：`Start`、`Comment`、`Delay`、`Set Variable`、`Return`、`Raise Error`

说明：
不要把“整个 API 类”直接当成一个节点，否则图会非常臃肿，也不利于导出 Python。

### 3.2 UI 布局决策
主窗口使用“四块核心区域”布局：

1. 左侧区
- 节点资源树
- 搜索框
- 节点分类切换

2. 中间区
- `NodeGraphQt` 画布

3. 右侧区
- 多个可折叠区域
- 至少包括：
  - 选中节点属性区
  - 选中节点运行状态区
  - Flow 校验结果区
  - 导出源码预览区

4. 下方区
- 日志展示窗口
- 建议使用 `QTabWidget` 或分栏日志视图，至少区分：
  - 全部日志
  - 运行日志
  - 校验日志
  - 导出日志

说明：
拖拽源放左侧更符合常见交互习惯；右侧更适合作为 Inspector / Properties / Preview。

### 3.3 右侧折叠面板决策
右侧多个区域必须是“可折叠”的。

实现方案建议：

- 优先使用自定义轻量 `CollapsibleSection`；
- 如实现成本更低，也可使用 `QToolBox`；
- 不要为了这个需求引入大型第三方 UI 框架。

### 3.4 执行模型决策
本阶段执行模型固定为：

- `Start` 节点作为流程起点；
- 控制流通过专用端口表达；
- 图必须保持无环；
- 运行前必须先做流程校验；
- 校验通过后才能执行；
- 执行时通过统一 `context` 容器保存会话、变量、日志引用和中间结果。

### 3.5 导出模型决策
导出 Python 时采用以下固定规则：

- 导出为独立 `.py` 文件；
- 文件中包含 `run_flow(context=None)`；
- 自动补齐所需 import；
- 导出后脚本应可脱离 GUI 独立运行；
- GUI 中“源码预览”看到的内容，必须与最终导出文件内容一致或只差文件头注释；
- 导出逻辑与 GUI 执行逻辑必须共享同一套节点语义。

---

## 4. 目录与文件结构要求
在 `@NodeGraphQt_notes/demo_02/` 中建议按如下结构组织代码，可根据实现需要微调，但总体职责不能混乱：

```text
demo_02/
├─ demo_02.py
├─ app_window.py
├─ node_registry.py
├─ workflow_runtime.py
├─ workflow_validator.py
├─ workflow_exporter.py
├─ ui/
│  ├─ collapsible_section.py
│  ├─ code_preview_dialog.py
│  └─ ...
├─ themes/
│  ├─ theme_dark.qss
│  └─ theme_light.qss
├─ assets/
│  └─ icons/
│     ├─ *.svg
├─ generated/
│  ├─ sample_flow.json
│  └─ sample_export.py
└─ Instruments_pythonic/
   ├─ __init__.py
   ├─ signal_generator.py
   ├─ digital_pattern_generator.py
   ├─ multi_serial_card.py
   └─ general.py
```

注意：
- 可以拆更多文件，但职责要清楚。
- `demo_02.py` 应作为入口文件。
- `generated/` 用于保存 smoke test 和示例导出物。

---

## 5. 仪器 API 设计要求（`Instruments_pythonic`）

### 5.1 总体要求
在 `Instruments_pythonic` 中实现 3 个模拟的、Python 化的、简化 IVI 风格虚拟仪器 API class：

1. 模拟信号发生器
2. 模拟数字模式发生器
3. 模拟多通道串口卡

这些类的函数体可以模拟实现，但接口风格要统一，参数命名尽量贴近 IVI 使用习惯。

### 5.2 统一风格要求
三个仪器类尽量统一具备以下生命周期与能力：

- `initialize(...)` 或 `open(...)`
- `close()`
- `reset()`
- `self_test()`
- `get_identity()` / `query_identity()`
- 若干 `configure_xxx(...)`
- 若干 `read(...)` / `measure(...)` / `query_xxx(...)`

建议统一参数命名风格：

- `resource_name`
- `channel`
- `enabled`
- `frequency`
- `amplitude`
- `offset`
- `phase`
- `sample_rate`
- `baud_rate`
- `timeout`

### 5.3 各仪器建议 API

#### 5.3.1 `signal_generator.py`
建议至少包含一个类，例如：

- `SimSignalGeneratorIvi`

建议至少实现以下方法：

- `initialize(resource_name, id_query=True, reset=False)`
- `get_identity()`
- `reset()`
- `self_test()`
- `configure_waveform(channel, waveform, frequency, amplitude, offset=0.0, phase=0.0)`
- `configure_output(channel, enabled)`
- `close()`

#### 5.3.2 `digital_pattern_generator.py`
建议至少包含一个类，例如：

- `SimDigitalPatternGeneratorIvi`

建议至少实现以下方法：

- `initialize(resource_name, id_query=True, reset=False)`
- `get_identity()`
- `reset()`
- `self_test()`
- `configure_timing(sample_rate, logic_level='3.3V')`
- `load_pattern(pattern_name, pattern_bits, loop_count=1)`
- `start_output()`
- `stop_output()`
- `query_status()`
- `close()`

#### 5.3.3 `multi_serial_card.py`
建议至少包含一个类，例如：

- `SimMultiSerialCardIvi`

建议至少实现以下方法：

- `initialize(resource_name, id_query=True, reset=False)`
- `get_identity()`
- `reset()`
- `self_test()`
- `open_port(channel, port_name, baud_rate, data_bits=8, parity='N', stop_bits=1, timeout=1.0)`
- `write(channel, data, encoding='utf-8')`
- `read(channel, size=0, timeout=None)`
- `close_port(channel)`
- `close()`

### 5.4 `general.py`
`general.py` 不要做成“硬件 API 类”，而是做成“通用流程语义支持层”或“通用节点运行辅助层”。

本阶段 `general.py` 中建议支持：

- `Start`
- `Comment`
- `Delay`
- `Set Variable`
- `Return`
- `Raise Error`

说明：
- `If / For / While / Get Variable` 可以预留扩展设计，但本次实现不要求做成完整可执行控制流节点。
- 如果实现 `Get Variable` 成本很低，可以一起纳入本阶段。

---

## 6. 节点资源树与节点模板要求

### 6.1 资源树不是源码树
左侧树控件展示的必须是“节点模板资源树”，不是文件树，不是类树，不是 Python 目录结构。

建议分类如下：

- `General`
  - `Start`
  - `Comment`
  - `Delay`
  - `Set Variable`
  - `Return`
  - `Raise Error`
- `Signal Generator`
  - `Open Session`
  - `Query Identity`
  - `Reset`
  - `Configure Waveform`
  - `Output Enable`
  - `Close Session`
- `Digital Pattern Generator`
  - `Open Session`
  - `Query Identity`
  - `Reset`
  - `Configure Timing`
  - `Load Pattern`
  - `Start Output`
  - `Stop Output`
  - `Close Session`
- `Multi Serial Card`
  - `Open Session`
  - `Open Port`
  - `Write`
  - `Read`
  - `Close Port`
  - `Close Session`

### 6.2 启动行为
demo 启动时必须自动加载左侧资源树。

### 6.3 拖拽行为
用户必须可以从左侧资源树把节点模板拖到中间画布，形成多个仪器或多个动作组成的流程。

---

## 7. 节点数据模型与运行时上下文要求

### 7.1 节点实例至少要包含以下信息
- 节点显示名
- 节点类型
- 节点分类
- 对应 API 类名
- 对应方法名
- 参数 schema
- 当前参数值
- 控制流输入/输出端口定义
- 导出 Python 所需元信息

### 7.2 会话绑定设计
为了支持一个 flow 中存在多个仪器实例，采用 `session_name` 设计：

- `Open Session` 节点创建某个会话；
- 其余动作节点通过 `session_name` 属性引用该会话；
- 运行时在 `context["sessions"]` 中保存会话对象。

建议运行时上下文结构至少包含：

```python
context = {
    "sessions": {},
    "variables": {},
    "last_result": None,
    "logs": [],
}
```

### 7.3 控制流端口设计
本阶段统一采用控制流端口：

- `flow_in`
- `flow_out`

本阶段不实现通用数据流线系统，中间值通过 `context["variables"]` 传递。

---

## 8. GUI 功能设计要求

### 8.1 菜单栏
菜单栏至少包含以下菜单分类：

- 文件
- 编辑
- 视图
- 运行
- 工具
- 语言
- 主题
- 帮助

### 8.2 工具栏
工具栏至少包含以下动作，且每个动作都要有对应 SVG 图标与 tooltip：

- 新建 flow
- 打开 flow
- 保存 flow
- 另存为
- 撤销
- 重做
- 自动排版
- 校验 flow
- 运行 flow
- 停止 / 取消运行（如果本阶段实现不了真正异步停止，可先做 UI 预留）
- 导出 Python
- 预览源码
- 语言切换
- 主题切换

### 8.3 右侧面板
右侧至少包含以下折叠区：

1. 选中节点属性区
2. 选中节点运行状态区
3. Flow 校验结果区
4. 导出源码预览区

如果实现顺手，也可以补充：

- 当前会话状态区
- 变量上下文区

### 8.4 日志窗口
下方必须有日志窗口。

建议能力：

- 显示时间戳；
- 区分日志来源；
- 支持清空；
- 运行、校验、导出时都要写日志；
- GUI 日志与控制台输出尽量保持一致。

---

## 9. 保存 / 加载 / 校验 / 导出要求

### 9.1 保存与加载
必须支持 node flow 保存为 JSON 和从 JSON 加载。

要求：

- 使用 `NodeGraphQt` 的 session 保存/加载能力；
- 补齐应用所需的额外元数据；
- 菜单和工具栏都要提供入口；
- 至少准备一个示例 flow 文件供 smoke test 使用。

### 9.2 流程校验
运行前必须先校验，校验通过后才允许执行。

至少检查：

- 是否存在 `Start` 节点；
- 关键控制流节点是否断开；
- 图中是否存在环；
- 关键参数是否缺失；
- 被引用的 `session_name` 是否存在；
- 导出代码是否可生成。

### 9.3 Python 导出
必须支持“所见即所得”的 Python 导出。

固定要求：

- 导出为独立 `.py` 文件；
- 文件中必须包含 `run_flow(context=None)`；
- 可选提供 `main()` 用于直接执行；
- 使用 `Instruments_pythonic` 下的 API 类；
- 生成的代码能脱离 GUI 直接运行；
- GUI 中必须有“源码预览对话框”显示导出源码。

---

## 10. 主题与国际化要求

### 10.1 语言切换
必须支持：

- 简体中文
- English

默认语言为简体中文。

建议切换范围包括：

- 菜单文本
- 工具栏文本
- 面板标题
- tooltip
- 状态栏文案
- 对话框标题

本阶段不要求翻译：

- 用户自行输入的节点名称
- 导出的 Python 变量名

### 10.2 主题切换
必须支持：

- 暗色主题（默认）
- 浅色主题

建议：

- 使用 QSS 管理主题；
- 至少提供 `theme_dark.qss` 与 `theme_light.qss`；
- 不要把颜色大量硬编码在各个控件实现里。

---

## 11. 本阶段不要求实现的内容
以下能力本阶段可以明确不做，避免范围失控：

- 真正的 `for` / `while` 回边循环执行
- 通用双向数据流端口系统
- 复杂结构化 `if/else` 图代码生成
- 多线程硬件执行与中途强制停止
- 插件热插拔
- 完整 IVI 标准复刻

说明：
本阶段重点是把 GUI、节点资源树、基础流程节点、仪器动作节点、保存 / 加载 / 导出 / 执行闭环先做稳。

---

## 12. 建议的最小可运行示例 flow
为了方便 smoke test，建议内置一条最小示例 flow，例如：

1. `Start`
2. `Open Signal Generator Session`
3. `Configure Waveform`
4. `Output Enable`
5. `Delay`
6. `Query Identity` 或 `Set Variable`
7. `Close Session`
8. `Return`

该 flow 应满足：

- 可在 GUI 中创建；
- 可执行；
- 可保存；
- 可重新加载；
- 可导出成 Python；
- 导出的 Python 可运行。

---

## 13. 验收标准
本次实现完成后，至少应满足以下验收标准：

1. `demo_02.py` 可启动 GUI；
2. 左侧资源树启动后自动出现；
3. 可以从资源树拖节点到 NodeGraphQt 画布；
4. 可以编辑节点参数；
5. 可以保存 flow；
6. 可以加载已保存 flow；
7. 可以对 flow 做校验；
8. 可以运行 flow，并在日志区输出信息；
9. 可以导出 Python 文件；
10. 可以在 GUI 中预览导出源码；
11. 支持中文 / English 切换；
12. 支持暗色 / 浅色主题切换；
13. 所有菜单、工具栏按钮、面板控件均有 tooltip；
14. 至少提供一个 headless 或半自动 smoke test 入口，并实际运行通过。

---

## 14. 启动与验证建议
建议主入口命令：

```bash
python "f:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02\demo_02.py"
```

建议增加 smoke test 入口：

```bash
python "f:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02\demo_02.py" --headless-smoke-test
```

smoke test 建议至少验证：

- GUI 相关对象可创建；
- 自动生成示例 flow；
- 校验通过；
- 运行通过；
- 保存 JSON 成功；
- 加载 JSON 成功；
- 导出 Python 成功；
- 导出的 Python 可运行。

---

## 15. 最终实现原则
本次 `demo_02` 的核心原则是：

> 先做出一个顺序执行型、可保存、可导出、可运行、可闭环验证的仪器图形化编程 demo；  
> 不在第一阶段把复杂控制流做过头；  
> 保证代码结构清晰，方便后续继续扩展到 `If / For / While / 更复杂导出器`。

后续如果需要第二阶段扩展，再在本版本稳定基础上继续加复杂控制流能力。
# 1. 需求
进一步的需求， 保留 @NodeGraphQt_notes/demo_01.py ,在 @NodeGraphQt_notes/ 创建demo_02 folder，然后创建新的demo，用于实现新的需求：
1. 遵循 @NodeGraphQt_notes/prompts_note.md 中的代码构建闭环
2. 在创建demo_02 folder中， 创建Instruments_pythonic folder，在该文件夹中存放3个模拟的python化的虚拟仪器API class，具体的API要遵循IVI仪器的接口/参数规则，API的函数体实现可以模拟实现，这部分你自己实现，实现模拟信号发生器/数字信号源头/多通道串口卡三个仪器的API
3. 2步骤实现以后，现在实现具体的应用，写入到demo_02.py中，具体的一些子模块可根据需创建新的python文件；
4. 先描述功能概述：该demo是要实现一个window界面，有菜单/工具栏/左中右分区三个分区，三个分区下边是日志展示窗口；中间分区中是NodeGraphQt的画布，右侧是可折叠（这个控件你知道的）的多个区域，分别是仪器树/选中节点的状态信息，以及你觉得必要的一些其他功能；
5. 菜单/工具栏目要根据需求添加/工具要有对应的svg小图标
6. demo启动时候自动加载仪器树到4中的右侧分区对应的控件中
7.拖动设备树中的对应API到中间的和画布，可以展示为NODE，uer可以拖动多个API到画布，形成一个仪器/或者多个仪器的控制流程
8. 可在 @Instruments_pythonic 中创建一个 general.py,实现常用的循环/分支/延时/return/raise error等必要的节点API，这类API的实现要考虑NODE图形化实现代码流程时候的便利性/可用性
9. 生成的仪器控制流程node flow，要可存储/可加装，菜单中要提供该功能
10. 要提供node flow 导出仪器API调用的python脚本的功能，也就是所见所得的NODE flow，可以导出可直接运行的函数，该函数是node flow的底层调用流程，你懂的；另外可用弹对话框的方式，通过点击工具栏的工具实现node flow对应的仪器API调用的python的源码展示
11. 通用的要求：所有的控件/提供鼠标悬停说明功能；所有的界面按钮/工具等可实现Englisg/简体中文切换，默认是中文；提供白色/暗色两个主题，默认暗色主题；

---

# 2. 基于当前理解的补充意见 / 不合理点 / 模糊点 / 建议

## 2.1 文字勘误
1. 第 9 条中的“可加装”建议改为“可加载”。
2. 第 7 条中的“uer”建议改为“user”。
3. 第 11 条中的“Englisg”建议改为“English”。
4. 第 2 条中的“数字信号源头”表述不清，建议明确为“数字信号发生器”或“数字模式发生器”或“数字 I/O 设备”，否则后续 API 设计会很模糊。

## 2.2 当前需求里最模糊、但必须先定清楚的点
1. “拖动设备树中的对应 API 到画布，可以展示为 NODE” 这句话现在语义不够清楚。
说明：
这里需要明确拖过去的到底是什么：
- 是“整个仪器类”拖成一个节点；
- 还是“仪器类下的方法”分别拖成多个动作节点；
- 还是“仪器会话节点 + 仪器动作节点”的组合。

建议：
不要把“整个 API 类”直接当成一个大节点，否则后续流程编排会非常笨重。更合理的方式是：
- 一个“Open/Initialize Instrument”节点负责建立会话；
- 多个“配置/输出/测量/关闭”动作节点负责具体调用；
- 所有动作节点共享一个仪器会话标识或上下文对象。

2. 左中右三区已经提到了，但左侧区做什么目前没有定义。
建议：
- 左侧：节点资源区 / 仪器与通用节点树 / 搜索区
- 中间：NodeGraphQt 画布
- 右侧：属性检查区、选中节点状态、运行时上下文、代码预览、校验结果

原因：
如果把“可拖拽的仪器树”放在右侧，交互上并不自然。通常拖拽源应放在左侧，右侧更适合作为“Inspector/Properties”。

3. “右侧是可折叠（这个控件你知道的）的多个区域” 这个要求太口语化，不足以指导实现。
建议明确控件方案：
- 优先建议使用 `QDockWidget` 或“自定义可折叠 Section 面板”
- 不建议为了一个折叠容器再额外引入大型外部依赖

建议先明确右侧至少包含哪些面板：
- 仪器/节点资源树
- 选中节点属性
- 节点运行状态
- 导出代码预览
- 图校验结果

## 2.3 从技术角度看，目前最不合理的点
1. 第 8 条要求加入“循环/分支/延时/return/raise error”等通用节点，这个需求本身合理，但它和当前 demo_01 的执行模型不是一个复杂度等级。
说明：
- `demo_01` 采用的是“无环 DAG + 拓扑排序 + 顺序执行”模型；
- 一旦你要支持真正的循环/分支，图就不再是简单 DAG；
- 导出 Python 代码时，也不再是简单的“按顺序拼语句”，而是要生成结构化代码块，例如 `if`、`for`、`while`、`return`、`raise`。

建议：
这个需求必须分阶段做，否则实现复杂度会突然暴涨。

建议拆成两个阶段：
- 第一阶段：先只支持顺序执行节点 + 简单条件节点 + 延时节点，不开放真正回边循环
- 第二阶段：再支持结构化控制流节点，例如 `If/Else`、`For Range`、`While`、`Return`、`Raise`

2. “要导出可直接运行的函数” 目前还不够具体。
需要明确：
- 导出的目标是一个 `.py` 模块，还是一个函数源码片段；
- 函数名是否固定；
- 是否自动补齐 import；
- 是否引用 `Instruments_pythonic` 下的 API 类；
- 是否允许导出后脱离 GUI 单独运行；
- 运行时上下文是函数内局部变量，还是外部 `context` 字典。

建议固定为：
- 导出一个独立 `.py` 文件；
- 文件内包含 `def run_flow(context=None): ...`；
- 自动生成所需 import；
- 保证导出后可直接运行；
- GUI 中再提供“源码预览对话框”查看同一份导出内容。

3. “遵循 IVI 仪器的接口/参数规则” 这个范围太大，如果不收敛，很容易把需求做成“伪 IVI”但又不够一致。
说明：
正式 IVI 体系很大，不同设备族接口风格也不完全一样；如果在这个 demo 里要完整复刻 IVI，会严重拉高工作量。

建议改成更可执行的目标：
- 实现“IVI 风格、Python 化、简化版”的统一 API；
- 三类仪器都遵循统一会话生命周期：
  - `initialize/open`
  - `reset`
  - `configure_xxx`
  - `read/measure/query`
  - `close`
- 参数命名保持一致，例如：
  - `resource_name`
  - `channel`
  - `enabled`
  - `amplitude`
  - `frequency`
  - `baud_rate`
  - `timeout`

## 2.4 强烈建议提前明确的数据模型
1. 需要明确“一个节点实例里保存什么”。
建议至少包含：
- 节点显示名
- 节点类型
- 所属仪器类型
- 对应 API 方法名
- 参数 schema
- 当前参数值
- 输入输出端口定义
- 导出 Python 所需的模板信息

2. 需要明确“运行时上下文”。
建议统一用一个 `context` 容器保存：
- 当前仪器会话对象
- 前面节点的输出值
- 运行日志引用
- 临时变量
- 异常状态

3. 需要明确“仪器树展示什么”。
建议不是直接展示“Python class 文件树”，而是展示“可拖拽节点模板树”。

建议树结构类似：
- Instruments
- Signal Generator
- Open Session
- Set Frequency
- Set Amplitude
- Output On/Off
- Digital Source
- Open Session
- Configure Pattern
- Start Output
- Serial Card
- Open Port
- Write
- Read
- General
- Delay
- If
- Return
- Raise Error

也就是说，树是“节点模板资源树”，而不是“源码浏览器”。

## 2.5 UI/交互方面的建议
1. 右侧“选中节点的状态信息”建议拆成两个区，不要混在一起：
- 属性编辑区
- 运行时状态区

因为这两个维度不同：
- 属性编辑区是设计时数据
- 运行状态区是执行时数据

2. 日志窗口建议不要只做一个纯文本框，最好预留日志等级和时间戳。
建议至少区分：
- 系统日志
- 图校验日志
- 执行日志
- 导出日志

3. 工具栏建议至少包含以下动作：
- 新建流程
- 打开流程
- 保存流程
- 另存为
- 撤销
- 重做
- 自动排版
- 校验流程
- 运行流程
- 停止运行
- 导出 Python
- 预览源码
- 语言切换
- 主题切换

4. “所有控件都有悬停说明”是对的，但建议同时明确：
- 菜单项有 tooltip
- 工具栏按钮有 tooltip
- 树节点有 tooltip
- 右侧属性项有 tooltip
- 节点内部控件有 tooltip

否则很容易出现“按钮有 tooltip，但节点属性没有”的不一致。

## 2.6 国际化和主题方面的建议
1. 语言切换需要明确切换范围。
建议明确以下内容都要切换：
- 菜单文本
- 工具栏文本
- 面板标题
- 对话框标题和按钮
- tooltip
- 状态栏文案

建议暂时不要切换以下内容：
- 用户自己输入的节点名称
- 导出的 Python 标识符

2. 主题切换建议用 QSS 统一做，不要散落在各个控件里硬编码颜色。
建议：
- `theme_dark.qss`
- `theme_light.qss`

节点颜色、日志颜色、工具栏样式、停靠区边框都尽量从主题层统一管理。

## 2.7 关于保存/加载/导出，建议明确成三类产物
建议不要只说“node flow 可存储/可加载”，而是明确三类文件：

1. 图工程文件
- 例如 `*.json`
- 保存 NodeGraphQt 的图结构和节点属性

2. 导出 Python 文件
- 例如 `*.py`
- 保存最终可运行的仪器调用函数

3. 可选的项目配置文件
- 例如 `project_meta.json`
- 保存主题、语言、最近文件、窗口布局等 UI 状态

这样架构更清晰，也更容易后续扩展。

## 2.8 关于执行引擎，建议补充一条强约束
建议新增一条需求：

“执行前必须先做流程校验，校验通过后才允许运行。”

校验至少包括：
- 是否存在起始节点
- 是否存在未连接的关键控制流节点
- 是否存在循环依赖（如果当前阶段不支持循环）
- 节点参数是否缺失
- 仪器会话节点是否在使用节点之前出现
- 导出代码是否能成功生成

原因：
`NodeGraphQt` 本身是编辑器，不会替你保证业务图一定能运行。校验层必须由应用自己补上。

## 2.9 关于 `general.py` 的建议
`general.py` 这个方向是对的，但建议不要只写“通用 API”，而要写成“通用流程节点语义集合”。

建议第一版先放这些：
- `Start`
- `Delay`
- `Comment/Note`
- `Set Variable`
- `Get Variable`
- `If`
- `Raise Error`
- `Return`

关于循环类节点，建议第一版谨慎处理：
- `For Range`
- `While`

因为它们一旦开放，就会直接影响：
- 图执行器
- 图校验器
- Python 导出器
- 可视化连线规则

## 2.10 关于仪器 API 的建议
三类模拟仪器 API 建议统一设计风格，不要三个类三种风格。

建议统一具备：
- 初始化/打开会话
- 关闭会话
- 标识查询
- Reset
- 自检
- 参数配置
- 运行/停止
- 读回/测量/查询

建议每个类都有：
- 明确的构造参数
- 清晰的属性
- 稳定的异常类型
- 模拟日志输出

对于串口卡，建议明确它到底是：
- “多通道串口卡设备”
还是
- “多个串口会话的统一管理器”

这两种设计会影响节点模型。

## 2.11 我建议的实现顺序
建议实际开发时按下面顺序推进，不要一口气全部做完：

第一阶段：
- 完成 `Instruments_pythonic` 三类模拟 API
- 搭出新的主窗口框架
- 左侧资源树 + 中间画布 + 右侧属性区 + 下方日志区
- 支持拖拽生成基础节点
- 支持保存/加载图
- 支持导出顺序型 Python

第二阶段：
- 补充右侧更多功能区
- 增加校验器
- 增加源码预览对话框
- 增加主题/语言切换

第三阶段：
- 增加 `If/Return/Raise`
- 再评估是否支持 `For/While`
- 若支持循环，再升级执行器和导出器

## 2.12 总结判断
我认为这份需求总体方向是对的，但当前存在三个关键问题：

1. 节点粒度没有定义清楚
如果不先明确“拖的是类、方法还是动作节点”，后面架构会反复返工。

2. 控制流复杂度被低估了
一旦支持循环/分支，就不再是简单顺序图，执行器和导出器都要升级。

3. UI 布局职责不够清晰
特别是左侧区未定义、右侧面板职责重叠、仪器树放右侧不太合理。

我的建议是：
先把 `demo_02` 的第一阶段目标收敛成“顺序执行型可视化仪器流程编辑器”，先把拖拽、属性、保存、导出、执行闭环做稳；然后再逐步扩展到结构化控制流和更复杂的通用节点。
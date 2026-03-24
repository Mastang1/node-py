# Demo 02 — 架构说明（Architect）

本文定义 **仪器图形化编程（Demo 02）** 的分层边界、扩展点与演进原则，供后续功能与多实例集成时对齐。

## 1. 目标与非目标

| 目标 | 非目标 |
|------|--------|
| UI 与「流程文档 / 运行语义」边界清晰 | 在本迭代内完全消除 `MainWindow` 上的所有业务方法 |
| 图编辑配置单点创建（工厂） | 引入完整 DI 容器 |
| 持久化策略可替换（平台层） | 支持云同步 / 多用户协作 |

## 2. 逻辑分层

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation — Qt MainWindow、对话框、资源树、属性编辑        │
│  职责：布局、信号槽、用户语言/主题、日志视图                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ 调用
┌───────────────────────────▼─────────────────────────────────┐
│  Application — FlowDocument（文档身份 + 脏标记）              │
│  职责：当前文件路径、与 undo 栈一致的 dirty 语义               │
└───────────────────────────┬─────────────────────────────────┘
                            │ 持有 ref
┌───────────────────────────▼─────────────────────────────────┐
│  Domain / Graph — NodeGraphQt + Workflow* 节点与校验/导出/运行  │
│  职责：图模型、执行语义（已有 workflow_* / flow_* 模块）         │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  Platform — QSettings 布局记忆、后续可接文件对话框封装等         │
│  职责：与 OS 交互的薄封装，无业务规则                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  Composition — graph_factory.build_configured_node_graph()   │
│  职责：注册节点、管道策略、布局方向、连线校验注入               │
└─────────────────────────────────────────────────────────────┘
```

## 3. 模块映射（当前）

| 层 | 模块 |
|----|------|
| Composition | `graph_factory.py` |
| Application | `application/flow_document.py` |
| Platform | `platform/settings_store.py` |
| Presentation | `app_window.py`（仍聚合运行/调试协调，后续可拆 `RunCoordinator`） |

导出：`workflow_exporter` 生成 visit 顺序的线性调用并包在 `run_flow()` 中，详见 `NodeGraphQt_notes/development_doc.md`。

## 4. 扩展点（建议顺序）

1. **新节点**：`nodes.py` + `node_registry.py`；工厂仅负责 `register_all_nodes`，不硬编码节点类型表。
2. **新持久化键**：仅改 `platform/settings_store.py` 或新增 `ThemeSettingsStore`。
3. **无头运行**：保持 `headless_flow_runner` / `WorkflowRuntime` 与 GUI 共用 domain 语义（见 `design_2.md` §16–17）。
4. **多文档**：为每个 `NodeGraph` 实例挂一个 `FlowDocument`，`MainWindow` 或 `WorkspaceController` 维护当前活动文档。

## 5. 不变量（Invariant）

- **跨线程**：调试/运行回写 UI 必须经过 `Signal` + `QueuedConnection`（见 `design_2.md` §17）。
- **视口**：禁止通过 `NodeGraph.fit_to_selection()` 间接缩小全局 `sceneRect`；使用应用层 `fitInView` 策略（见 `design_2.md` §18）。
- **流程语义**：运行、导出、调试共享同一套「状态机 + 端口值表」模型。

## 6. 版本与文档

- 发布版本见仓库根 `VERSION`；与本文件重大结构变更同步更新本节日期与 `design_2.md` 对应章节。

*Last updated: 2026-03 — architecture extraction (graph_factory, FlowDocument, settings_store).*

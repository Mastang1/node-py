from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from Qt import QtCore, QtGui, QtWidgets
from NodeGraphQt.constants import LayoutDirectionEnum, PortTypeEnum

from .common import (
    DEFAULT_EXPORT_PATH,
    DEFAULT_FLOW_PATH,
    GENERATED_DIR,
    ICONS_DIR,
    LANG_EN,
    LANG_ZH,
    SUPPORTED_THEMES,
    THEME_DARK,
    THEME_LIGHT,
    THEMES_DIR,
    data_type_compatible,
    ensure_directory,
    ensure_parent_directory,
    pretty_json,
)
from .application.flow_document import FlowDocument
from .graph_factory import build_configured_node_graph
from .node_registry import (
    api_node_template_count,
    configure_graph_port_constraints,
    ensure_instrument_api_registered,
)
from .platform.settings_store import MainLayoutSettingsStore
from .nodes import (
    BooleanConstantNode,
    BooleanLogicNode,
    BooleanNotNode,
    CloseSignalGeneratorSessionNode,
    CommentNode,
    CompareNumberNode,
    CompareTextNode,
    ConfigureSignalGeneratorWaveformNode,
    DelayNode,
    FloatConstantNode,
    OpenSignalGeneratorSessionNode,
    QuerySignalGeneratorIdentityNode,
    RaiseErrorNode,
    ReadIntVariableNode,
    ReturnNode,
    SetVariableNode,
    SignalGeneratorOutputEnableNode,
    StartNode,
    TextConstantNode,
    IntegerConstantNode,
    LastResultIndexNode,
    MathBinaryNode,
    WriteVariableFromInputNode,
    WorkflowNode,
)
from .ui.code_preview_dialog import CodePreviewDialog
from .ui.connection_manager_dialog import ConnectionManagerDialog
from .ui.help_dialog import show_help_browser
from .ui.property_editor import NodePropertyEditor
from .ui.resource_tree import ResourceTreeWidget
from .flow_debug_worker import FlowDebugWorker
from .flow_run_controller import FlowRunController
from .workflow_debug import DebugSession
from .workflow_exporter import WorkflowExporter
from .workflow_validator import WorkflowValidator


TEXTS = {
    "app_title": {LANG_ZH: "Demo 02 - 仪器图形化编程", LANG_EN: "Demo 02 - Instrument Flow Programming"},
    "menu_file": {LANG_ZH: "文件", LANG_EN: "File"},
    "menu_edit": {LANG_ZH: "编辑", LANG_EN: "Edit"},
    "menu_view": {LANG_ZH: "视图", LANG_EN: "View"},
    "menu_run": {LANG_ZH: "运行", LANG_EN: "Run"},
    "menu_tools": {LANG_ZH: "工具", LANG_EN: "Tools"},
    "menu_language": {LANG_ZH: "语言", LANG_EN: "Language"},
    "menu_theme": {LANG_ZH: "主题", LANG_EN: "Theme"},
    "menu_help": {LANG_ZH: "帮助", LANG_EN: "Help"},
    "menu_debug": {LANG_ZH: "调试", LANG_EN: "Debug"},
    "start_debug": {LANG_ZH: "开始调试", LANG_EN: "Start Debugging"},
    "debug_step": {LANG_ZH: "单步执行", LANG_EN: "Step Over"},
    "debug_continue": {LANG_ZH: "继续运行", LANG_EN: "Continue"},
    "stop_debug": {LANG_ZH: "停止调试", LANG_EN: "Stop Debugger"},
    "toggle_breakpoint": {LANG_ZH: "切换断点", LANG_EN: "Toggle Breakpoint"},
    "section_debug": {LANG_ZH: "调试：当前节点对应 Python", LANG_EN: "Debug: Python for current node"},
    "debug_hint": {
        LANG_ZH: "开始调试后，此处显示与导出脚本一致的节点函数体（emit_python）。",
        LANG_EN: "After starting debug, the node's emit_python body (same as export) appears here.",
    },
    "about_app": {LANG_ZH: "关于", LANG_EN: "About"},
    "about_body": {
        LANG_ZH: "Demo 02 — 仪器图形化编程。\n支持流程运行、单步调试与 Python 导出。",
        LANG_EN: "Demo 02 — instrument visual programming.\nRun flows, step-debug, and export Python.",
    },
    "new_flow": {LANG_ZH: "新建流程", LANG_EN: "New Flow"},
    "open_flow": {LANG_ZH: "打开流程", LANG_EN: "Open Flow"},
    "save_flow": {LANG_ZH: "保存流程", LANG_EN: "Save Flow"},
    "save_flow_as": {LANG_ZH: "流程另存为", LANG_EN: "Save Flow As"},
    "undo": {LANG_ZH: "撤销", LANG_EN: "Undo"},
    "redo": {LANG_ZH: "重做", LANG_EN: "Redo"},
    "auto_layout": {LANG_ZH: "自动排版", LANG_EN: "Auto Layout"},
    "center_flow": {LANG_ZH: "画布居中", LANG_EN: "Center Flow"},
    "arrange_row": {LANG_ZH: "单行排列", LANG_EN: "Arrange Row"},
    "arrange_column": {LANG_ZH: "单列排列", LANG_EN: "Arrange Column"},
    "validate_flow": {LANG_ZH: "校验流程", LANG_EN: "Validate Flow"},
    "run_flow": {LANG_ZH: "运行流程", LANG_EN: "Run Flow"},
    "stop_flow": {LANG_ZH: "停止流程", LANG_EN: "Stop Flow"},
    "export_python": {LANG_ZH: "导出 Python", LANG_EN: "Export Python"},
    "preview_code": {LANG_ZH: "预览源码", LANG_EN: "Preview Source"},
    "inspect_connections": {LANG_ZH: "连接关系检查", LANG_EN: "Inspect Connections"},
    "toggle_language": {LANG_ZH: "切换语言", LANG_EN: "Toggle Language"},
    "toggle_theme": {LANG_ZH: "切换主题", LANG_EN: "Toggle Theme"},
    "load_sample": {LANG_ZH: "加载示例流程", LANG_EN: "Load Sample Flow"},
    "load_instruments": {LANG_ZH: "加载仪器 API", LANG_EN: "Load Instrument API"},
    "section_properties": {LANG_ZH: "选中节点属性", LANG_EN: "Selected Node Properties"},
    "section_runtime": {LANG_ZH: "节点运行状态", LANG_EN: "Node Runtime State"},
    "section_validation": {LANG_ZH: "流程校验结果", LANG_EN: "Validation Results"},
    "section_preview": {LANG_ZH: "导出源码预览", LANG_EN: "Export Source Preview"},
    "tab_all_logs": {LANG_ZH: "全部日志", LANG_EN: "All Logs"},
    "tab_run_logs": {LANG_ZH: "运行日志", LANG_EN: "Run Logs"},
    "tab_validate_logs": {LANG_ZH: "校验日志", LANG_EN: "Validation Logs"},
    "tab_export_logs": {LANG_ZH: "导出日志", LANG_EN: "Export Logs"},
    "resource_tree": {LANG_ZH: "节点资源树", LANG_EN: "Node Resource Tree"},
    "preview_dialog": {LANG_ZH: "导出源码预览", LANG_EN: "Export Source Preview"},
    "connections_dialog": {LANG_ZH: "连接线管理", LANG_EN: "Connection Manager"},
    "close": {LANG_ZH: "关闭", LANG_EN: "Close"},
    "locate_source": {LANG_ZH: "定位源节点", LANG_EN: "Locate Source"},
    "locate_target": {LANG_ZH: "定位目标节点", LANG_EN: "Locate Target"},
    "highlight_connection": {LANG_ZH: "高亮连接", LANG_EN: "Highlight Connection"},
    "delete_nodes": {LANG_ZH: "删除节点", LANG_EN: "Delete Nodes"},
    "rotate_nodes": {LANG_ZH: "节点旋转", LANG_EN: "Rotate Nodes"},
    "disconnect_connections": {LANG_ZH: "断开连接", LANG_EN: "Disconnect Connections"},
    "disconnect_inputs": {LANG_ZH: "断开输入连接", LANG_EN: "Disconnect Inputs"},
    "disconnect_outputs": {LANG_ZH: "断开输出连接", LANG_EN: "Disconnect Outputs"},
    "align_left": {LANG_ZH: "左对齐", LANG_EN: "Align Left"},
    "align_top": {LANG_ZH: "上对齐", LANG_EN: "Align Top"},
    "distribute_horizontal": {LANG_ZH: "水平分布", LANG_EN: "Distribute Horizontally"},
    "distribute_vertical": {LANG_ZH: "垂直分布", LANG_EN: "Distribute Vertically"},
    "confirm_unsaved_title": {LANG_ZH: "保存当前流程", LANG_EN: "Save Current Flow"},
    "confirm_unsaved_message": {
        LANG_ZH: "当前流程有未保存修改，是否先保存后再继续？",
        LANG_EN: "The current flow has unsaved changes. Save before continuing?",
    },
    "no_runtime_state": {LANG_ZH: "当前节点暂无运行状态。", LANG_EN: "No runtime state for the current node."},
    "preview_placeholder": {LANG_ZH: "校验或导出后，这里显示源码预览。", LANG_EN: "Source preview appears here after validate/export."},
    "validation_placeholder": {LANG_ZH: "点击“校验流程”查看结果。", LANG_EN: "Click 'Validate Flow' to see results."},
    "runtime_not_supported": {LANG_ZH: "第一阶段未实现异步停止，当前仅保留界面入口。", LANG_EN: "Async stop is not implemented in phase one; the UI entry is reserved only."},
    "help_menu_flow": {LANG_ZH: "节点流程说明", LANG_EN: "Node Flow Guide"},
    "help_menu_debug": {LANG_ZH: "运行与调试", LANG_EN: "Run & Debug Help"},
    "help_menu_shortcuts": {LANG_ZH: "键盘快捷方式", LANG_EN: "Keyboard Shortcuts"},
    "help_html_flow": {
        LANG_ZH: (
            "<html><body style='font-size:11pt;'>"
            "<h2>节点流程（Node Flow）</h2>"
            "<p>画布上的图被解释为<strong>状态机</strong>：节点执行后按<strong>流程出口</strong>决定下一跳；"
            "数据经<strong>数据端口</strong>在节点间传递，与流程连线不同。</p>"
            "<ul>"
            "<li><b>校验流程</b>：运行前检查孤立节点、端口类型、循环与导出一致性等。</li>"
            "<li><b>运行流程</b>：子进程执行 headless 运行器，主界面通过日志更新状态，避免阻塞 UI。</li>"
            "<li><b>导出 Python</b>：按遍历顺序生成线性调用（如 <code>delay(1.0)</code>、<code>comment(&quot;…&quot;)</code>），封装在 <code>run_flow()</code> 内便于测试嵌入。</li>"
            "<li><b>连接管理</b>：可定位、高亮流程/数据连接，快速排查错误连线。</li>"
            "</ul>"
            "<p><b>画布居中</b>：将选中节点适配到视口；未选节点时框选全部。"
            "实现上仅缩放视口（fitInView），不会缩小整张场景导致窗口异常。</p>"
            "</body></html>"
        ),
        LANG_EN: (
            "<html><body style='font-size:11pt;'>"
            "<h2>Node flow</h2>"
            "<p>The graph is a <strong>state machine</strong>: after each node runs, the "
            "<strong>flow output</strong> chooses the next step. <strong>Data ports</strong> carry values "
            "between nodes and are separate from flow wires.</p>"
            "<ul>"
            "<li><b>Validate Flow</b>: checks orphans, port types, cycles, and export consistency before run.</li>"
            "<li><b>Run Flow</b>: uses a subprocess runner; the UI stays responsive via log updates.</li>"
            "<li><b>Export Python</b>: linear calls in visit order (e.g. <code>delay</code>, <code>comment</code>) inside <code>run_flow()</code> for easy test embedding.</li>"
            "<li><b>Connection Manager</b>: locate and highlight flow/data links for troubleshooting.</li>"
            "</ul>"
            "<p><b>Center Flow</b>: frames the selection in the viewport (or all nodes if none selected). "
            "It uses <code>fitInView</code> only and does not shrink the global scene rect.</p>"
            "</body></html>"
        ),
    },
    "help_html_debug": {
        LANG_ZH: (
            "<html><body style='font-size:11pt;'>"
            "<h2>运行与调试</h2>"
            "<p><b>运行</b>与<b>调试</b>共用同一套流程语义；调试额外提供断点、单步与当前节点 Python 预览。</p>"
            "<ul>"
            "<li><b>开始调试</b>：在后台线程中执行；日志与节点高亮通过信号回到主线程。</li>"
            "<li><b>单步 / 继续</b>：在断点或每步暂停处推进；右侧「调试」页显示与导出一致的 <code>emit_python</code> 片段。</li>"
            "<li><b>断点</b>：对选中节点切换；暂停时当前节点会高亮。</li>"
            "<li><b>停止</b>：结束调试会话并恢复节点默认样式（在适用情况下）。</li>"
            "</ul>"
            "<p>若刚点击「开始调试」后立即「继续」，请勿依赖线程 <code>isRunning()</code> 门槛——"
            "实现上已保证首节点不会因竞态永久阻塞。</p>"
            "</body></html>"
        ),
        LANG_EN: (
            "<html><body style='font-size:11pt;'>"
            "<h2>Run &amp; debug</h2>"
            "<p><b>Run</b> and <b>debug</b> share the same flow semantics. Debug adds breakpoints, "
            "step/continue, and a Python preview for the current node.</p>"
            "<ul>"
            "<li><b>Start Debugging</b>: runs on a worker thread; logs and highlights are delivered via signals.</li>"
            "<li><b>Step / Continue</b>: advance from breakpoints or each step; the Debug tab shows the same "
            "<code>emit_python</code> body as export.</li>"
            "<li><b>Breakpoints</b>: toggle on selected nodes; the paused node is highlighted.</li>"
            "<li><b>Stop</b>: ends the session and restores default node styling where applicable.</li>"
            "</ul>"
            "<p>Continue must not depend on <code>QThread.isRunning()</code> right after start—a race there "
            "would block the first node forever; the app guards against that.</p>"
            "</body></html>"
        ),
    },
    "help_html_shortcuts": {
        LANG_ZH: (
            "<html><body style='font-size:11pt;'>"
            "<h2>键盘快捷方式</h2>"
            "<table border='0' cellpadding='6'>"
            "<tr><td><b>F5</b></td><td>运行流程</td></tr>"
            "<tr><td><b>Shift+F5</b></td><td>停止调试</td></tr>"
            "<tr><td><b>F8</b></td><td>调试：继续运行</td></tr>"
            "<tr><td><b>F10</b></td><td>调试：单步</td></tr>"
            "<tr><td><b>F9</b></td><td>切换断点（需先选中节点）</td></tr>"
            "</table>"
            "<p>完整命令仍可通过菜单与工具栏访问；语言与主题在「语言」「主题」菜单中切换。</p>"
            "</body></html>"
        ),
        LANG_EN: (
            "<html><body style='font-size:11pt;'>"
            "<h2>Keyboard shortcuts</h2>"
            "<table border='0' cellpadding='6'>"
            "<tr><td><b>F5</b></td><td>Run flow</td></tr>"
            "<tr><td><b>Shift+F5</b></td><td>Stop debugging</td></tr>"
            "<tr><td><b>F8</b></td><td>Debug: continue</td></tr>"
            "<tr><td><b>F10</b></td><td>Debug: step</td></tr>"
            "<tr><td><b>F9</b></td><td>Toggle breakpoint (select node(s) first)</td></tr>"
            "</table>"
            "<p>All actions are also available from menus and toolbars; use Language / Theme menus to switch UI.</p>"
            "</body></html>"
        ),
    },
}


class Demo02Window(QtWidgets.QMainWindow):
    """主界面：Presentation 层。图配置见 graph_factory；文档路径/脏标记见 FlowDocument；布局持久化见 platform。"""

    debug_log_requested = QtCore.Signal(str, str)
    debug_node_state_requested = QtCore.Signal(str, str, dict)

    def __init__(self) -> None:
        super().__init__()
        self.current_language = LANG_ZH
        self.current_theme = THEME_DARK
        self.current_selected_node: WorkflowNode | None = None
        self.node_runtime_states: dict[str, dict[str, Any]] = {}
        self.node_visual_defaults: dict[str, dict[str, Any]] = {}
        self.last_rendered_code = ""
        self.context_commands: dict[str, Any] = {}
        self.debug_session = DebugSession()
        self._debug_worker: FlowDebugWorker | None = None
        self._debug_paused_node_id: str | None = None
        self._run_controller: FlowRunController | None = None
        self._run_temp_json: Path | None = None
        self._main_h_splitter: QtWidgets.QSplitter | None = None
        self._main_v_splitter: QtWidgets.QSplitter | None = None
        self._layout_restored: bool = False

        self.graph = build_configured_node_graph(
            self._viewer_connection_validation,
            self._viewer_connection_feedback,
        )
        self._document = FlowDocument(self.graph)
        self._layout_store = MainLayoutSettingsStore()

        self._build_widgets()
        self._build_actions()
        self._build_menus()
        self._build_toolbar()
        self._build_layout()
        self._register_context_menus()
        self._wire_signals()
        self.retranslate_ui()
        self.apply_theme(THEME_DARK)
        self.build_sample_flow(prompt_if_dirty=False)
        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()

    @property
    def current_flow_path(self) -> Path | None:
        return self._document.path

    @current_flow_path.setter
    def current_flow_path(self, value: Path | None) -> None:
        self._document.path = value

    def t(self, key: str) -> str:
        return TEXTS[key][self.current_language]

    def _icon(self, name: str) -> QtGui.QIcon:
        return QtGui.QIcon(str(ICONS_DIR / f"{name}.svg"))

    def _build_widgets(self) -> None:
        self.resource_tree = ResourceTreeWidget()
        self.resource_tree.setToolTip(self.t("resource_tree"))

        self.property_editor = NodePropertyEditor()

        self.runtime_text = QtWidgets.QPlainTextEdit()
        self.runtime_text.setReadOnly(True)

        self.validation_text = QtWidgets.QPlainTextEdit()
        self.validation_text.setReadOnly(True)

        self.preview_text = QtWidgets.QPlainTextEdit()
        self.preview_text.setReadOnly(True)

        self.debug_code_text = QtWidgets.QTextEdit()
        self.debug_code_text.setReadOnly(True)
        dbg_font = QtGui.QFont("Consolas")
        if not dbg_font.exactMatch():
            dbg_font = QtGui.QFont("Monospace")
        dbg_font.setStyleHint(QtGui.QFont.Monospace)
        self.debug_code_text.setFont(dbg_font)
        self.debug_code_text.setMinimumHeight(140)

        _expand = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.property_editor.setSizePolicy(_expand)
        self.runtime_text.setSizePolicy(_expand)
        self.validation_text.setSizePolicy(_expand)
        self.preview_text.setSizePolicy(_expand)
        self.debug_code_text.setSizePolicy(_expand)

        def _tab_page(inner: QtWidgets.QWidget) -> QtWidgets.QWidget:
            page = QtWidgets.QWidget()
            pl = QtWidgets.QVBoxLayout(page)
            pl.setContentsMargins(4, 4, 4, 4)
            pl.addWidget(inner)
            return page

        self.right_panel = QtWidgets.QTabWidget()
        self.right_panel.setDocumentMode(True)
        self.right_panel.setMinimumWidth(260)
        self.right_panel.addTab(_tab_page(self.property_editor), "")
        self.right_panel.addTab(_tab_page(self.runtime_text), "")
        self.right_panel.addTab(_tab_page(self.debug_code_text), "")
        self.right_panel.addTab(_tab_page(self.validation_text), "")
        self.right_panel.addTab(_tab_page(self.preview_text), "")

        self.log_tabs = QtWidgets.QTabWidget()
        self.log_editors = {
            "all": QtWidgets.QPlainTextEdit(),
            "run": QtWidgets.QPlainTextEdit(),
            "validate": QtWidgets.QPlainTextEdit(),
            "export": QtWidgets.QPlainTextEdit(),
        }
        for editor in self.log_editors.values():
            editor.setReadOnly(True)
        self.log_tabs.addTab(self.log_editors["all"], "")
        self.log_tabs.addTab(self.log_editors["run"], "")
        self.log_tabs.addTab(self.log_editors["validate"], "")
        self.log_tabs.addTab(self.log_editors["export"], "")

        self.preview_dialog = CodePreviewDialog(self)
        self.connection_manager_dialog = ConnectionManagerDialog(self)

        self.runtime_text.setPlainText(self.t("no_runtime_state"))
        self.validation_text.setPlainText(self.t("validation_placeholder"))
        self.preview_text.setPlainText(self.t("preview_placeholder"))
        self.debug_code_text.setPlaceholderText(self.t("debug_hint"))

    def _build_actions(self) -> None:
        self.actions: dict[str, QtGui.QAction] = {}
        action_specs = {
            "new_flow": "new",
            "open_flow": "open",
            "save_flow": "save",
            "save_flow_as": "save_as",
            "undo": "undo",
            "redo": "redo",
            "auto_layout": "layout",
            "center_flow": "center",
            "arrange_row": "row",
            "arrange_column": "column",
            "validate_flow": "validate",
            "run_flow": "run",
            "stop_flow": "stop",
            "export_python": "export",
            "preview_code": "preview",
            "inspect_connections": "layout",
            "toggle_language": "language",
            "toggle_theme": "theme",
            "load_sample": "preview",
            "load_instruments": "instruments",
            "start_debug": "debug_run",
            "debug_step": "debug_step",
            "debug_continue": "debug_continue",
            "stop_debug": "debug_stop",
            "toggle_breakpoint": "breakpoint",
            "about_app": "validate",
        }
        for key, icon_name in action_specs.items():
            action = QtGui.QAction(self._icon(icon_name), "", self)
            action.setObjectName(key)
            self.actions[key] = action

    def _build_menus(self) -> None:
        self.menu_file = self.menuBar().addMenu("")
        self.menu_edit = self.menuBar().addMenu("")
        self.menu_view = self.menuBar().addMenu("")
        self.menu_run = self.menuBar().addMenu("")
        self.menu_tools = self.menuBar().addMenu("")
        self.menu_language = self.menuBar().addMenu("")
        self.menu_theme = self.menuBar().addMenu("")
        self.menu_help = self.menuBar().addMenu("")

        self.menu_file.addAction(self.actions["new_flow"])
        self.menu_file.addAction(self.actions["open_flow"])
        self.menu_file.addAction(self.actions["save_flow"])
        self.menu_file.addAction(self.actions["save_flow_as"])
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.actions["load_instruments"])
        self.menu_file.addAction(self.actions["load_sample"])

        self.menu_edit.addAction(self.actions["undo"])
        self.menu_edit.addAction(self.actions["redo"])
        self.menu_edit.addAction(self.actions["auto_layout"])
        self.menu_edit.addAction(self.actions["arrange_row"])
        self.menu_edit.addAction(self.actions["arrange_column"])

        self.menu_view.addAction(self.actions["center_flow"])

        self.menu_run.addAction(self.actions["validate_flow"])
        self.menu_run.addAction(self.actions["run_flow"])
        self.menu_run.addAction(self.actions["stop_flow"])
        self.menu_run.addSeparator()
        self.submenu_debug = self.menu_run.addMenu("")
        self.submenu_debug.addAction(self.actions["start_debug"])
        self.submenu_debug.addAction(self.actions["debug_step"])
        self.submenu_debug.addAction(self.actions["debug_continue"])
        self.submenu_debug.addAction(self.actions["stop_debug"])
        self.submenu_debug.addSeparator()
        self.submenu_debug.addAction(self.actions["toggle_breakpoint"])

        self.menu_tools.addAction(self.actions["export_python"])
        self.menu_tools.addAction(self.actions["preview_code"])
        self.menu_tools.addAction(self.actions["inspect_connections"])

        self.menu_language.addAction(self.actions["toggle_language"])
        self.menu_theme.addAction(self.actions["toggle_theme"])

        self._help_action_flow = QtGui.QAction(self)
        self._help_action_flow.triggered.connect(lambda: self._open_help("flow"))
        self._help_action_debug = QtGui.QAction(self)
        self._help_action_debug.triggered.connect(lambda: self._open_help("debug"))
        self._help_action_shortcuts = QtGui.QAction(self)
        self._help_action_shortcuts.triggered.connect(lambda: self._open_help("shortcuts"))
        self.menu_help.addAction(self._help_action_flow)
        self.menu_help.addAction(self._help_action_debug)
        self.menu_help.addAction(self._help_action_shortcuts)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.actions["about_app"])

    def _build_toolbar(self) -> None:
        tb_style = QtCore.Qt.ToolButtonTextBesideIcon
        icon_sz = QtCore.QSize(22, 22)

        self.toolbar_file = self.addToolBar("toolbar_file")
        self.toolbar_file.setMovable(False)
        self.toolbar_file.setToolButtonStyle(tb_style)
        self.toolbar_file.setIconSize(icon_sz)
        self.toolbar_file.addAction(self.actions["new_flow"])
        self.toolbar_file.addAction(self.actions["open_flow"])
        self.toolbar_file.addAction(self.actions["save_flow"])
        self.toolbar_file.addAction(self.actions["save_flow_as"])

        self.toolbar_edit = self.addToolBar("toolbar_edit")
        self.toolbar_edit.setMovable(False)
        self.toolbar_edit.setToolButtonStyle(tb_style)
        self.toolbar_edit.setIconSize(icon_sz)
        self.toolbar_edit.addAction(self.actions["undo"])
        self.toolbar_edit.addAction(self.actions["redo"])
        self.toolbar_edit.addSeparator()
        self.toolbar_edit.addAction(self.actions["auto_layout"])
        self.toolbar_edit.addAction(self.actions["center_flow"])
        self.toolbar_edit.addAction(self.actions["arrange_row"])
        self.toolbar_edit.addAction(self.actions["arrange_column"])

        self.toolbar_run = self.addToolBar("toolbar_run")
        self.toolbar_run.setMovable(False)
        self.toolbar_run.setToolButtonStyle(tb_style)
        self.toolbar_run.setIconSize(icon_sz)
        self.toolbar_run.addAction(self.actions["validate_flow"])
        self.toolbar_run.addAction(self.actions["run_flow"])
        self.toolbar_run.addAction(self.actions["stop_flow"])
        self.toolbar_run.addSeparator()
        self.toolbar_run.addAction(self.actions["export_python"])
        self.toolbar_run.addAction(self.actions["preview_code"])
        self.toolbar_run.addAction(self.actions["inspect_connections"])

        self.toolbar_debug = self.addToolBar("toolbar_debug")
        self.toolbar_debug.setMovable(False)
        self.toolbar_debug.setToolButtonStyle(tb_style)
        self.toolbar_debug.setIconSize(icon_sz)
        self.toolbar_debug.addAction(self.actions["start_debug"])
        self.toolbar_debug.addAction(self.actions["debug_step"])
        self.toolbar_debug.addAction(self.actions["debug_continue"])
        self.toolbar_debug.addAction(self.actions["stop_debug"])
        self.toolbar_debug.addSeparator()
        self.toolbar_debug.addAction(self.actions["toggle_breakpoint"])

        self.toolbar_misc = self.addToolBar("toolbar_misc")
        self.toolbar_misc.setMovable(False)
        self.toolbar_misc.setToolButtonStyle(tb_style)
        self.toolbar_misc.setIconSize(icon_sz)
        self.toolbar_misc.addAction(self.actions["load_instruments"])
        self.toolbar_misc.addAction(self.actions["load_sample"])
        self.toolbar_misc.addSeparator()
        self.toolbar_misc.addAction(self.actions["toggle_language"])
        self.toolbar_misc.addAction(self.actions["toggle_theme"])

        self._update_execution_action_states()

    def _build_layout(self) -> None:
        left_container = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.resource_tree)

        self._main_h_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._main_h_splitter.addWidget(left_container)
        self._main_h_splitter.addWidget(self.graph.widget)
        self._main_h_splitter.addWidget(self.right_panel)
        self._main_h_splitter.setSizes([280, 920, 360])
        self._main_h_splitter.setStretchFactor(0, 0)
        self._main_h_splitter.setStretchFactor(1, 1)
        self._main_h_splitter.setStretchFactor(2, 0)
        for _i in range(3):
            self._main_h_splitter.setCollapsible(_i, False)

        self._main_v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._main_v_splitter.addWidget(self._main_h_splitter)
        self._main_v_splitter.addWidget(self.log_tabs)
        self._main_v_splitter.setSizes([760, 220])
        self._main_v_splitter.setStretchFactor(0, 1)
        self._main_v_splitter.setStretchFactor(1, 0)
        for _j in range(2):
            self._main_v_splitter.setCollapsible(_j, False)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self._main_v_splitter)
        self.setCentralWidget(central)

    def _register_context_menus(self) -> None:
        graph_menu = self.graph.get_context_menu("graph")
        nodes_menu = self.graph.get_context_menu("nodes")

        if graph_menu is not None:
            graph_menu.add_separator()
            self.context_commands["center_flow"] = graph_menu.add_command("Center Flow", self._graph_context_center_flow)
            self.context_commands["arrange_row"] = graph_menu.add_command("Arrange Row", self._graph_context_arrange_row)
            self.context_commands["arrange_column"] = graph_menu.add_command(
                "Arrange Column", self._graph_context_arrange_column
            )
            self.context_commands["inspect_connections"] = graph_menu.add_command(
                "Inspect Connections", self._graph_context_inspect_connections
            )
            self.context_commands["align_left"] = graph_menu.add_command("Align Left", self._graph_context_align_left)
            self.context_commands["align_top"] = graph_menu.add_command("Align Top", self._graph_context_align_top)
            self.context_commands["distribute_horizontal"] = graph_menu.add_command(
                "Distribute Horizontally", self._graph_context_distribute_horizontal
            )
            self.context_commands["distribute_vertical"] = graph_menu.add_command(
                "Distribute Vertically", self._graph_context_distribute_vertical
            )
            self.context_commands["disconnect_connections"] = graph_menu.add_command(
                "Disconnect Connections", self._graph_context_disconnect_connections
            )

        if nodes_menu is not None:
            self.context_commands["delete_nodes"] = nodes_menu.add_command(
                "Delete Nodes",
                self._nodes_context_delete,
                node_class=WorkflowNode,
            )
            self.context_commands["rotate_nodes"] = nodes_menu.add_command(
                "Rotate Nodes",
                self._nodes_context_rotate,
                node_class=WorkflowNode,
            )
            self.context_commands["disconnect_node_connections"] = nodes_menu.add_command(
                "Disconnect Connections",
                self._nodes_context_disconnect,
                node_class=WorkflowNode,
            )
            self.context_commands["disconnect_inputs"] = nodes_menu.add_command(
                "Disconnect Inputs",
                self._nodes_context_disconnect_inputs,
                node_class=WorkflowNode,
            )
            self.context_commands["disconnect_outputs"] = nodes_menu.add_command(
                "Disconnect Outputs",
                self._nodes_context_disconnect_outputs,
                node_class=WorkflowNode,
            )
            self.context_commands["toggle_breakpoint"] = nodes_menu.add_command(
                "Toggle Breakpoint",
                self._nodes_context_toggle_breakpoint,
                node_class=WorkflowNode,
            )

    def _wire_signals(self) -> None:
        self.actions["new_flow"].triggered.connect(lambda: self.new_flow())
        self.actions["open_flow"].triggered.connect(self.open_flow)
        self.actions["save_flow"].triggered.connect(self.save_flow)
        self.actions["save_flow_as"].triggered.connect(self.save_flow_as)
        self.actions["undo"].triggered.connect(self.graph.undo_stack().undo)
        self.actions["redo"].triggered.connect(self.graph.undo_stack().redo)
        self.actions["auto_layout"].triggered.connect(self.auto_layout_flow)
        self.actions["center_flow"].triggered.connect(self.center_flow)
        self.actions["arrange_row"].triggered.connect(self.arrange_nodes_row)
        self.actions["arrange_column"].triggered.connect(self.arrange_nodes_column)
        self.actions["validate_flow"].triggered.connect(self.validate_flow)
        self.actions["run_flow"].triggered.connect(self.run_flow)
        self.actions["stop_flow"].triggered.connect(self.stop_flow)
        self.actions["export_python"].triggered.connect(self.export_python)
        self.actions["preview_code"].triggered.connect(self.preview_code)
        self.actions["inspect_connections"].triggered.connect(self.inspect_connections)
        self.actions["toggle_language"].triggered.connect(self.toggle_language)
        self.actions["toggle_theme"].triggered.connect(self.toggle_theme)
        self.actions["load_sample"].triggered.connect(lambda: self.build_sample_flow())
        self.actions["load_instruments"].triggered.connect(self.load_instrument_api_nodes)
        self.actions["start_debug"].triggered.connect(self.start_debug_flow)
        self.actions["debug_step"].triggered.connect(self.debug_step_over)
        self.actions["debug_continue"].triggered.connect(self.debug_continue_run)
        self.actions["stop_debug"].triggered.connect(self.stop_debug_flow)
        self.actions["toggle_breakpoint"].triggered.connect(self.toggle_debug_breakpoint)
        self.actions["about_app"].triggered.connect(self.show_about_dialog)

        self.graph.node_selected.connect(self.on_node_selected)
        self.graph.node_double_clicked.connect(self.on_node_selected)
        self.graph.node_created.connect(self.on_node_created)
        self.graph.nodes_deleted.connect(self.on_nodes_deleted)
        self.graph.property_changed.connect(self.on_graph_property_changed)
        self.graph.port_connected.connect(self.on_port_connected)
        self.graph.port_disconnected.connect(
            lambda in_port, out_port: self.log("run", f"断开连接: {out_port.node().name()} -> {in_port.node().name()}")
        )
        self.graph.undo_stack().indexChanged.connect(lambda _index: self._update_window_title())

        self.debug_log_requested.connect(self.log, QtCore.Qt.QueuedConnection)
        self.debug_node_state_requested.connect(self._apply_debug_node_state_main, QtCore.Qt.QueuedConnection)

        QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self, activated=self.run_flow)
        QtWidgets.QShortcut(QtGui.QKeySequence("F8"), self, activated=self.debug_continue_run)
        QtWidgets.QShortcut(QtGui.QKeySequence("F10"), self, activated=self.debug_step_over)
        QtWidgets.QShortcut(QtGui.QKeySequence("F9"), self, activated=self.toggle_debug_breakpoint)
        QtWidgets.QShortcut(QtGui.QKeySequence("Shift+F5"), self, activated=self.stop_debug_flow)

    def retranslate_ui(self) -> None:
        self.menu_file.setTitle(self.t("menu_file"))
        self.menu_edit.setTitle(self.t("menu_edit"))
        self.menu_view.setTitle(self.t("menu_view"))
        self.menu_run.setTitle(self.t("menu_run"))
        self.menu_tools.setTitle(self.t("menu_tools"))
        self.menu_language.setTitle(self.t("menu_language"))
        self.menu_theme.setTitle(self.t("menu_theme"))
        self.menu_help.setTitle(self.t("menu_help"))
        self.submenu_debug.setTitle(self.t("menu_debug"))

        for key, action in self.actions.items():
            if key in TEXTS:
                text = self.t(key)
                action.setText(text)
                action.setToolTip(text)
                action.setStatusTip(text)

        for key, command in self.context_commands.items():
            text_key = key if key in TEXTS else "disconnect_connections" if "disconnect" in key else key
            if text_key in TEXTS:
                text = self.t(text_key)
                command.qaction.setText(text)
                command.qaction.setToolTip(text)
                command.qaction.setStatusTip(text)

        self.right_panel.setTabText(0, self.t("section_properties"))
        self.right_panel.setTabText(1, self.t("section_runtime"))
        self.right_panel.setTabText(2, self.t("section_debug"))
        self.right_panel.setTabText(3, self.t("section_validation"))
        self.right_panel.setTabText(4, self.t("section_preview"))
        self.debug_code_text.setPlaceholderText(self.t("debug_hint"))

        self._help_action_flow.setText(self.t("help_menu_flow"))
        self._help_action_flow.setToolTip(self.t("help_menu_flow"))
        self._help_action_flow.setStatusTip(self.t("help_menu_flow"))
        self._help_action_debug.setText(self.t("help_menu_debug"))
        self._help_action_debug.setToolTip(self.t("help_menu_debug"))
        self._help_action_debug.setStatusTip(self.t("help_menu_debug"))
        self._help_action_shortcuts.setText(self.t("help_menu_shortcuts"))
        self._help_action_shortcuts.setToolTip(self.t("help_menu_shortcuts"))
        self._help_action_shortcuts.setStatusTip(self.t("help_menu_shortcuts"))

        self.log_tabs.setTabText(0, self.t("tab_all_logs"))
        self.log_tabs.setTabText(1, self.t("tab_run_logs"))
        self.log_tabs.setTabText(2, self.t("tab_validate_logs"))
        self.log_tabs.setTabText(3, self.t("tab_export_logs"))

        self.preview_dialog.set_title(self.t("preview_dialog"))
        self.preview_dialog.set_close_text(self.t("close"))
        self.connection_manager_dialog.set_title(self.t("connections_dialog"))
        self.connection_manager_dialog.set_close_text(self.t("close"))
        self.connection_manager_dialog.set_action_texts(
            self.t("locate_source"),
            self.t("locate_target"),
            self.t("highlight_connection"),
        )
        self.connection_manager_dialog.set_filters(
            [
                ("全部连接" if self.current_language == LANG_ZH else "All Connections", "all"),
                ("流程连接" if self.current_language == LANG_ZH else "Flow Connections", "flow"),
                ("数据连接" if self.current_language == LANG_ZH else "Data Connections", "data"),
                ("无效连接" if self.current_language == LANG_ZH else "Invalid Connections", "invalid"),
            ]
        )
        self.connection_manager_dialog.set_callbacks(
            locate_source=self._locate_connection_source,
            locate_target=self._locate_connection_target,
            highlight=self._highlight_connection_entry,
        )

        self.resource_tree.retranslate(self.current_language)
        self.property_editor.retranslate(self.current_language)

        if not self.current_selected_node:
            self.runtime_text.setPlainText(self.t("no_runtime_state"))
        if not self.last_rendered_code:
            self.preview_text.setPlainText(self.t("preview_placeholder"))
        if not self.validation_text.toPlainText().strip():
            self.validation_text.setPlainText(self.t("validation_placeholder"))
        self._update_window_title()

    def apply_theme(self, theme_name: str) -> None:
        if theme_name not in SUPPORTED_THEMES:
            theme_name = THEME_DARK
        qss_path = THEMES_DIR / f"theme_{theme_name}.qss"
        if qss_path.is_file():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        if theme_name == THEME_DARK:
            self.graph.set_background_color(13, 18, 32)
            self.graph.set_grid_color(35, 48, 75)
        else:
            self.graph.set_background_color(244, 247, 255)
            self.graph.set_grid_color(205, 219, 242)
        self.current_theme = theme_name
        self.log("all", f"切换主题: {theme_name}")

    def toggle_theme(self) -> None:
        self.apply_theme(THEME_LIGHT if self.current_theme == THEME_DARK else THEME_DARK)

    def toggle_language(self) -> None:
        self.current_language = LANG_EN if self.current_language == LANG_ZH else LANG_ZH
        self.retranslate_ui()
        self.log("all", f"切换语言: {self.current_language}")

    def _flow_display_name(self) -> str:
        if self.current_flow_path is not None:
            return self.current_flow_path.name
        return self.t("new_flow")

    def _is_flow_dirty(self) -> bool:
        return self._document.is_dirty()

    def _mark_flow_clean(self) -> None:
        self._document.mark_clean()
        self._update_window_title()

    def _update_window_title(self) -> None:
        suffix = " *" if self._is_flow_dirty() else ""
        self.setWindowTitle(f"{self.t('app_title')} | {self._flow_display_name()}{suffix}")

    def _confirm_can_abandon_current_flow(self) -> bool:
        if not self._is_flow_dirty():
            return True
        box = QtWidgets.QMessageBox(self)
        box.setIcon(QtWidgets.QMessageBox.Warning)
        box.setWindowTitle(self.t("confirm_unsaved_title"))
        box.setText(self.t("confirm_unsaved_message"))
        box.setInformativeText(self._flow_display_name())
        box.setStandardButtons(
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel
        )
        box.setDefaultButton(QtWidgets.QMessageBox.Save)
        result = box.exec()
        if result == QtWidgets.QMessageBox.Save:
            return self.save_flow() is not None
        if result == QtWidgets.QMessageBox.Discard:
            return True
        return False

    def _target_nodes(self, preferred: list[WorkflowNode] | None = None) -> list[WorkflowNode]:
        selected = [node for node in self.graph.selected_nodes() if isinstance(node, WorkflowNode)]
        if selected:
            nodes = selected
        elif preferred:
            nodes = preferred
        else:
            nodes = [node for node in self.graph.all_nodes() if isinstance(node, WorkflowNode)]
        return sorted(
            nodes,
            key=lambda node: (round(node.y_pos(), 3), round(node.x_pos(), 3), node.name(), node.id),
        )

    def _graph_context_center_flow(self, _graph: object) -> None:
        self.center_flow()

    def _graph_context_arrange_row(self, _graph: object) -> None:
        self.arrange_nodes_row()

    def _graph_context_arrange_column(self, _graph: object) -> None:
        self.arrange_nodes_column()

    def _graph_context_inspect_connections(self, _graph: object) -> None:
        self.inspect_connections()

    def _graph_context_align_left(self, _graph: object) -> None:
        self.align_nodes_left()

    def _graph_context_align_top(self, _graph: object) -> None:
        self.align_nodes_top()

    def _graph_context_distribute_horizontal(self, _graph: object) -> None:
        self.distribute_nodes_horizontal()

    def _graph_context_distribute_vertical(self, _graph: object) -> None:
        self.distribute_nodes_vertical()

    def _graph_context_disconnect_connections(self, _graph: object) -> None:
        self.disconnect_selected_connections()

    def _nodes_context_delete(self, graph: object, node: WorkflowNode | None) -> None:
        targets = self._target_nodes([node] if isinstance(node, WorkflowNode) else None)
        if not targets:
            return
        graph.delete_nodes(targets)
        self.log("all", f"已删除 {len(targets)} 个节点。")

    def _nodes_context_rotate(self, _graph: object, node: WorkflowNode | None) -> None:
        targets = self._target_nodes([node] if isinstance(node, WorkflowNode) else None)
        if not targets:
            return
        rotated = 0
        for current in targets:
            current_direction = current.layout_direction()
            target_direction = (
                LayoutDirectionEnum.VERTICAL.value
                if current_direction == LayoutDirectionEnum.HORIZONTAL.value
                else LayoutDirectionEnum.HORIZONTAL.value
            )
            current.set_layout_direction(target_direction)
            rotated += 1
        self.log("all", f"已旋转 {rotated} 个节点。")

    def _nodes_context_disconnect(self, _graph: object, node: WorkflowNode | None) -> None:
        targets = self._target_nodes([node] if isinstance(node, WorkflowNode) else None)
        if not targets:
            return
        disconnected = self._disconnect_node_connections(targets, mode="all")
        self.log("all", f"已清理 {len(targets)} 个节点的连接，共处理 {disconnected} 条连接端。")

    def _nodes_context_disconnect_inputs(self, _graph: object, node: WorkflowNode | None) -> None:
        targets = self._target_nodes([node] if isinstance(node, WorkflowNode) else None)
        if not targets:
            return
        disconnected = self._disconnect_node_connections(targets, mode="inputs")
        self.log("all", f"已断开 {len(targets)} 个节点的输入连接，共处理 {disconnected} 条连接端。")

    def _nodes_context_disconnect_outputs(self, _graph: object, node: WorkflowNode | None) -> None:
        targets = self._target_nodes([node] if isinstance(node, WorkflowNode) else None)
        if not targets:
            return
        disconnected = self._disconnect_node_connections(targets, mode="outputs")
        self.log("all", f"已断开 {len(targets)} 个节点的输出连接，共处理 {disconnected} 条连接端。")

    def log(self, channel: str, message: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
        line = f"{timestamp} | {message}"
        if os.environ.get("DEMO02_QUIET_SMOKE") != "1":
            self.log_editors["all"].appendPlainText(line)
            if channel in self.log_editors and channel != "all":
                self.log_editors[channel].appendPlainText(line)
            print(line)
            self.statusBar().showMessage(message, 5000)

    def on_node_selected(self, node: WorkflowNode) -> None:
        if not isinstance(node, WorkflowNode):
            self.current_selected_node = None
            self.property_editor.set_node(None)
            self.update_runtime_panel()
            return
        self.current_selected_node = node
        self.property_editor.set_node(node)
        self.update_runtime_panel()

    def on_node_created(self, node: WorkflowNode) -> None:
        if not isinstance(node, WorkflowNode):
            return
        if self.current_language == LANG_EN and (node.name() == node.NODE_NAME or node.name().startswith(f"{node.NODE_NAME} ")):
            node.set_name(node.display_name(LANG_EN))
        node.set_icon(node.icon_path())
        self.node_visual_defaults[node.id] = {
            "color": node.model.color,
            "border_color": tuple(node.view.border_color),
            "text_color": tuple(node.view.text_color),
        }
        if hasattr(node.view, "setToolTip"):
            node.view.setToolTip(node.description(self.current_language))
        self.log("all", f"创建节点: {node.name()}")

    def on_nodes_deleted(self, node_ids: list[str]) -> None:
        for node_id in node_ids:
            self.node_runtime_states.pop(node_id, None)
            self.node_visual_defaults.pop(node_id, None)
            self.debug_session.set_breakpoint(node_id, False)
        if self._debug_paused_node_id in node_ids:
            self._debug_paused_node_id = None
        if self.current_selected_node and self.current_selected_node.id in node_ids:
            self.current_selected_node = None
            self.property_editor.set_node(None)
            self.update_runtime_panel()

    def on_graph_property_changed(self, node: WorkflowNode, prop_name: str, prop_value: object) -> None:
        if not isinstance(node, WorkflowNode):
            return
        if self.current_selected_node and node.id == self.current_selected_node.id:
            self.property_editor.update_current_node_property(prop_name, prop_value)
            if prop_name == "name":
                self.property_editor.set_node(node)
        if hasattr(node.view, "setToolTip"):
            node.view.setToolTip(node.description(self.current_language))

    def _port_from_view_item(self, port_item: Any) -> Any:
        node = self.graph.get_node_by_id(port_item.node.id)
        if not isinstance(node, WorkflowNode):
            return None
        if port_item.port_type == PortTypeEnum.IN.value:
            return node.inputs().get(port_item.name)
        return node.outputs().get(port_item.name)

    def _viewer_connection_validation(self, from_port_item: Any, to_port_item: Any) -> tuple[bool, str]:
        from_port = self._port_from_view_item(from_port_item)
        to_port = self._port_from_view_item(to_port_item)
        if from_port is None or to_port is None:
            return True, ""
        if from_port_item.port_type == PortTypeEnum.OUT.value and to_port_item.port_type == PortTypeEnum.IN.value:
            return self._connection_is_valid(to_port, from_port)
        if from_port_item.port_type == PortTypeEnum.IN.value and to_port_item.port_type == PortTypeEnum.OUT.value:
            return self._connection_is_valid(from_port, to_port)
        return False, "端口方向不正确。"

    def _viewer_connection_feedback(self, message: str) -> None:
        if message:
            self.statusBar().showMessage(message, 3000)
            return
        self.statusBar().clearMessage()

    def _connection_is_valid(self, in_port: Any, out_port: Any) -> tuple[bool, str]:
        input_node = in_port.node()
        output_node = out_port.node()
        if not isinstance(input_node, WorkflowNode) or not isinstance(output_node, WorkflowNode):
            return True, ""

        input_flow_spec = input_node.flow_input_spec_from_label(in_port.name())
        output_flow_spec = output_node.flow_output_spec_from_label(out_port.name())
        if input_flow_spec is not None or output_flow_spec is not None:
            if input_flow_spec is None or output_flow_spec is None:
                return False, f"流程端口不能与数据端口混连: {output_node.name()} -> {input_node.name()}"
            return True, ""

        input_data_spec = input_node.data_input_spec_from_label(in_port.name())
        output_data_spec = output_node.data_output_spec_from_label(out_port.name())
        if input_data_spec is None or output_data_spec is None:
            return False, f"未识别的端口连接: {output_node.name()} -> {input_node.name()}"
        if not data_type_compatible(output_data_spec.data_type, input_data_spec.data_type):
            return (
                False,
                f"类型不兼容: {output_node.name()} 的 {output_data_spec.label}({output_data_spec.data_type}) "
                f"不能连接到 {input_node.name()} 的 {input_data_spec.label}({input_data_spec.data_type})",
            )
        return True, ""

    def _collect_connection_entries(self) -> list[dict[str, str]]:
        seen: set[tuple[str, str, str, str]] = set()
        entries: list[dict[str, str]] = []
        for source_node in self.graph.all_nodes():
            if not isinstance(source_node, WorkflowNode):
                continue
            for output_port in source_node.outputs().values():
                for input_port in output_port.connected_ports():
                    target_node = input_port.node()
                    if not isinstance(target_node, WorkflowNode):
                        continue
                    key = (source_node.id, output_port.name(), target_node.id, input_port.name())
                    if key in seen:
                        continue
                    seen.add(key)
                    is_valid, message = self._connection_is_valid(input_port, output_port)
                    kind = "flow" if source_node.flow_output_spec_from_label(output_port.name()) else "data"
                    if not is_valid:
                        kind = "invalid"
                    entries.append(
                        {
                            "kind": kind,
                            "source_id": source_node.id,
                            "source_name": source_node.name(),
                            "source_port": output_port.name(),
                            "target_id": target_node.id,
                            "target_name": target_node.name(),
                            "target_port": input_port.name(),
                            "message": message,
                            "summary": (
                                f"{source_node.name()}[{output_port.name()}] -> "
                                f"{target_node.name()}[{input_port.name()}]"
                                + (f" | {message}" if message else "")
                            ),
                        }
                    )
        return entries

    def _frame_nodes_in_viewport(self, nodes: list[Any] | None = None, *, margin: float = 80.0) -> None:
        """Fit the viewport to nodes without shrinking the global scene rect (avoids main-window glitches)."""
        viewer = self.graph.viewer()
        if nodes is None:
            raw = self.graph.selected_nodes() or self.graph.all_nodes()
        else:
            raw = nodes
        views = [n.view for n in raw if n is not None and getattr(n, "view", None) is not None]
        if not views:
            return
        rect = viewer._combined_rect(views)  # same geometry as NodeGraphQt zoom_to_nodes
        rect = rect.adjusted(-margin, -margin, margin, margin)
        if rect.width() < 1.0 or rect.height() < 1.0:
            return
        viewer.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def _open_help(self, topic: str) -> None:
        html = TEXTS[f"help_html_{topic}"][self.current_language]
        show_help_browser(self, self.t(f"help_menu_{topic}"), html)

    def _locate_nodes(self, node_ids: list[str]) -> None:
        nodes = [self.graph.get_node_by_id(node_id) for node_id in node_ids]
        targets = [node for node in nodes if isinstance(node, WorkflowNode)]
        if not targets:
            return
        self.graph.clear_selection()
        for node in targets:
            node.set_selected(True)
        self._frame_nodes_in_viewport(targets)

    def _find_pipe_item(self, entry: dict[str, Any]) -> Any:
        source_node = self.graph.get_node_by_id(entry.get("source_id"))
        target_node = self.graph.get_node_by_id(entry.get("target_id"))
        if not isinstance(source_node, WorkflowNode) or not isinstance(target_node, WorkflowNode):
            return None
        output_port = source_node.outputs().get(entry.get("source_port", ""))
        input_port = target_node.inputs().get(entry.get("target_port", ""))
        if output_port is None or input_port is None:
            return None
        for pipe in getattr(output_port.view, "connected_pipes", []):
            if pipe.input_port == input_port.view and pipe.output_port == output_port.view:
                return pipe
        return None

    def _locate_connection_source(self, entry: dict[str, Any]) -> None:
        self._locate_nodes([str(entry.get("source_id", ""))])

    def _locate_connection_target(self, entry: dict[str, Any]) -> None:
        self._locate_nodes([str(entry.get("target_id", ""))])

    def _highlight_connection_entry(self, entry: dict[str, Any]) -> None:
        self._locate_nodes([str(entry.get("source_id", "")), str(entry.get("target_id", ""))])
        pipe_item = self._find_pipe_item(entry)
        if pipe_item is not None:
            pipe_item.setSelected(True)
            self.statusBar().showMessage(entry.get("summary", ""), 4000)

    def inspect_connections(self) -> None:
        self.connection_manager_dialog.set_title(self.t("connections_dialog"))
        self.connection_manager_dialog.set_close_text(self.t("close"))
        self.connection_manager_dialog.set_entries(self._collect_connection_entries())
        self.connection_manager_dialog.exec()

    def on_port_connected(self, in_port: Any, out_port: Any) -> None:
        is_valid, message = self._connection_is_valid(in_port, out_port)
        if not is_valid:
            in_port.disconnect_from(out_port)
            self.log("all", f"连接已拒绝: {message}")
            return
        self.log("run", f"建立连接: {out_port.node().name()} -> {in_port.node().name()}")

    def on_runtime_node_state(self, node: WorkflowNode, status: str, payload: dict[str, Any]) -> None:
        self.node_runtime_states[node.id] = {"status": status, **payload}
        self._apply_runtime_visual(node, status)
        if self.current_selected_node and node.id == self.current_selected_node.id:
            self.update_runtime_panel()

    def _apply_debug_node_state_main(self, node_id: str, status: str, payload: dict[str, Any]) -> None:
        node = self.graph.get_node_by_id(node_id)
        if isinstance(node, WorkflowNode):
            self.on_runtime_node_state(node, status, payload)

    def update_runtime_panel(self) -> None:
        if not self.current_selected_node:
            self.runtime_text.setPlainText(self.t("no_runtime_state"))
            return
        payload = self.node_runtime_states.get(self.current_selected_node.id)
        if not payload:
            self.runtime_text.setPlainText(self.t("no_runtime_state"))
            return
        self.runtime_text.setPlainText(pretty_json(payload))

    def _refresh_node_visuals(self) -> None:
        for node in self.graph.all_nodes():
            if not isinstance(node, WorkflowNode):
                continue
            node.set_icon(node.icon_path())
            self.node_visual_defaults[node.id] = {
                "color": node.model.color,
                "border_color": tuple(node.view.border_color),
                "text_color": tuple(node.view.text_color),
            }
            if hasattr(node.view, "setToolTip"):
                node.view.setToolTip(node.description(self.current_language))

    def _apply_runtime_visual(self, node: WorkflowNode, status: str) -> None:
        default_visual = self.node_visual_defaults.get(node.id)
        if default_visual is None:
            return
        border_color = default_visual["border_color"]
        text_color = default_visual["text_color"]
        if status == "running":
            border_color = (58, 191, 248, 255)
            text_color = (235, 248, 255, 255)
        elif status == "success":
            border_color = (34, 197, 94, 255)
            text_color = (232, 252, 241, 255)
        elif status == "error":
            border_color = (239, 68, 68, 255)
            text_color = (255, 235, 235, 255)
        node.view.border_color = border_color
        node.model.border_color = border_color
        node.view.text_color = text_color
        node.model.text_color = text_color
        node.view.draw_node()

    def _reset_runtime_visuals(self) -> None:
        for node in self.graph.all_nodes():
            if not isinstance(node, WorkflowNode):
                continue
            default_visual = self.node_visual_defaults.get(node.id)
            if default_visual is None:
                continue
            node.view.border_color = default_visual["border_color"]
            node.model.border_color = default_visual["border_color"]
            node.view.text_color = default_visual["text_color"]
            node.model.text_color = default_visual["text_color"]
            node.view.draw_node()

    def _set_node_border_and_text(
        self, node: WorkflowNode, border_rgba: tuple[int, int, int, int], text_rgba: tuple[int, int, int, int]
    ) -> None:
        node.view.border_color = border_rgba
        node.model.border_color = border_rgba
        node.view.text_color = text_rgba
        node.model.text_color = text_rgba
        node.view.draw_node()

    def _restore_base_node_visual(self, node: WorkflowNode) -> None:
        default_visual = self.node_visual_defaults.get(node.id)
        if default_visual is None:
            return
        self._set_node_border_and_text(node, default_visual["border_color"], default_visual["text_color"])

    def _apply_breakpoint_overlays(self) -> None:
        for node in self.graph.all_nodes():
            if not isinstance(node, WorkflowNode):
                continue
            if self._debug_paused_node_id == node.id:
                continue
            if self.debug_session.has_breakpoint(node.id):
                self._set_node_border_and_text(
                    node,
                    (217, 119, 6, 255),
                    (255, 247, 237, 255),
                )
            else:
                self._restore_base_node_visual(node)

    def _clear_debug_pause_highlight(self) -> None:
        if not self._debug_paused_node_id:
            return
        node = self.graph.get_node_by_id(self._debug_paused_node_id)
        self._debug_paused_node_id = None
        if isinstance(node, WorkflowNode):
            if self.debug_session.has_breakpoint(node.id):
                self._set_node_border_and_text(
                    node,
                    (217, 119, 6, 255),
                    (255, 247, 237, 255),
                )
            else:
                self._restore_base_node_visual(node)

    def _apply_debug_pause_highlight(self, node: WorkflowNode) -> None:
        self._clear_debug_pause_highlight()
        self._debug_paused_node_id = node.id
        self._set_node_border_and_text(
            node,
            (147, 51, 234, 255),
            (243, 232, 255, 255),
        )

    def _apply_python_to_text_edit(self, widget: QtWidgets.QTextEdit, code: str) -> None:
        try:
            from pygments import highlight
            from pygments.formatters import HtmlFormatter
            from pygments.lexers import PythonLexer
        except ImportError:
            widget.setPlainText(code)
            return

        formatter = HtmlFormatter(style="monokai", noclasses=True, nowrap=False)
        body = highlight(code, PythonLexer(), formatter)
        css = formatter.get_style_defs(".highlight")
        wrapped = (
            "<html><head><meta charset=\"utf-8\">"
            f"<style>pre {{ margin: 0; }} {css}</style></head>"
            f"<body style=\"background:#272822;color:#f8f8f2;\"><div class=\"highlight\">{body}</div></body></html>"
        )
        widget.setHtml(wrapped)

    def _update_execution_action_states(self) -> None:
        dbg_busy = self._debug_worker is not None and self._debug_worker.isRunning()
        run_busy = self._run_controller is not None and self._run_controller.is_running()
        blocked = dbg_busy or run_busy
        self.actions["start_debug"].setEnabled(not blocked)
        self.actions["run_flow"].setEnabled(not blocked)
        self.actions["debug_step"].setEnabled(dbg_busy)
        self.actions["debug_continue"].setEnabled(dbg_busy)
        self.actions["stop_debug"].setEnabled(dbg_busy)
        self.actions["stop_flow"].setEnabled(run_busy or dbg_busy)

    def _on_debug_paused(self, info: Any) -> None:
        # Headless smoke sets DEMO02_QUIET_SMOKE: skip heavy syntax highlight / graph selection that can
        # stall or deadlock with offscreen + processEvents polling.
        if os.environ.get("DEMO02_QUIET_SMOKE") == "1":
            return
        self._apply_debug_pause_highlight(info.node)
        self._apply_python_to_text_edit(self.debug_code_text, info.snippet_text)
        self.graph.clear_selection()
        info.node.set_selected(True)
        self.log("run", f"[调试] 暂停于步骤 {info.step_index}: {info.node.name()} — {info.export_function_name}()")

    def _on_debug_run_finished(self, result: Any) -> None:
        if self._debug_worker is not None:
            self._debug_worker.deleteLater()
            self._debug_worker = None
        self._clear_debug_pause_highlight()
        self._apply_breakpoint_overlays()
        self._update_execution_action_states()
        if result is not None:
            self.update_runtime_panel()
            self.log("run", f"[调试] 完成，返回值: {result.context.return_value!r}")
            try:
                vars_text = pretty_json(result.context.variables)
            except (TypeError, ValueError):
                vars_text = repr(result.context.variables)
            self.log("run", f"[调试] 变量: {vars_text}")
        else:
            self.log("run", "[调试] 已停止（未完成整个流程）。")
        self.statusBar().showMessage(self.t("stop_debug"), 3000)

    def _on_debug_run_failed(self, message: str) -> None:
        if self._debug_worker is not None:
            self._debug_worker.deleteLater()
            self._debug_worker = None
        self._clear_debug_pause_highlight()
        self._apply_breakpoint_overlays()
        self._update_execution_action_states()
        self.log("run", f"[调试] 失败: {message}")
        QtWidgets.QMessageBox.critical(self, self.t("stop_debug"), message)

    def show_about_dialog(self) -> None:
        QtWidgets.QMessageBox.information(self, self.t("about_app"), self.t("about_body"))

    def create_flow_debug_worker(self) -> FlowDebugWorker:
        """Build a wired :class:`FlowDebugWorker`; call ``start()`` when ready (allows extra signal hooks first)."""
        worker = FlowDebugWorker(
            self.graph,
            lambda ch, msg: self.debug_log_requested.emit(ch, msg),
            self.current_language,
            self.debug_session,
            lambda node, st, pl: self.debug_node_state_requested.emit(node.id, st, pl),
            self,
        )
        worker.paused_at.connect(self._on_debug_paused, QtCore.Qt.QueuedConnection)
        # Must be queued: emitted from worker thread; direct slots would touch GUI on wrong thread.
        worker.run_finished.connect(self._on_debug_run_finished, QtCore.Qt.QueuedConnection)
        worker.run_failed.connect(self._on_debug_run_failed, QtCore.Qt.QueuedConnection)
        return worker

    def start_debug_flow(self) -> None:
        if self._debug_worker is not None and self._debug_worker.isRunning():
            self.log("run", "[调试] 已在运行中。")
            return
        if not self.validate_flow():
            self.log("run", "[调试] 校验未通过，无法开始。")
            return
        self.node_runtime_states.clear()
        self._reset_runtime_visuals()
        self._apply_breakpoint_overlays()
        self.debug_session.reset_for_new_run()

        worker = self.create_flow_debug_worker()
        self._debug_worker = worker
        self._update_execution_action_states()
        self.log("run", "[调试] 开始。使用「单步」或「继续」前进；F10 / F8 快捷方式可用。")
        worker.start()

    def debug_step_over(self) -> None:
        if self._debug_worker is None or not self._debug_worker.isRunning():
            return
        self.debug_session.step_over()

    def debug_continue_run(self) -> None:
        # Do not require isRunning(): right after QThread.start() the flag can still be false for a tick,
        # and we must still arm go_free so the first wait_before_node() does not block forever.
        if self._debug_worker is None:
            return
        self.debug_session.continue_run()

    def stop_debug_flow(self) -> None:
        if self._debug_worker is None:
            return
        self.debug_session.stop()

    def toggle_debug_breakpoint(self) -> None:
        targets = self._target_nodes(None)
        if not targets:
            self.statusBar().showMessage(self.t("toggle_breakpoint") + " — " + ("请先选择节点" if self.current_language == LANG_ZH else "Select node(s) first"), 4000)
            return
        for node in targets:
            enabled = self.debug_session.toggle_breakpoint(node.id)
            self.log("run", f"[调试] 断点 {'开启' if enabled else '关闭'}: {node.name()}")
        self._apply_breakpoint_overlays()

    def _nodes_context_toggle_breakpoint(self, _graph: object, node: WorkflowNode | None) -> None:
        targets = self._target_nodes([node] if isinstance(node, WorkflowNode) else None)
        if not targets:
            return
        for n in targets:
            self.debug_session.toggle_breakpoint(n.id)
        self._apply_breakpoint_overlays()

    def new_flow(self, prompt_if_dirty: bool = True) -> bool:
        if prompt_if_dirty and not self._confirm_can_abandon_current_flow():
            return False
        self.graph.clear_session()
        self.current_flow_path = None
        self.current_selected_node = None
        self.node_runtime_states.clear()
        self.node_visual_defaults.clear()
        self.property_editor.set_node(None)
        self.runtime_text.setPlainText(self.t("no_runtime_state"))
        self.validation_text.setPlainText(self.t("validation_placeholder"))
        self.preview_text.setPlainText(self.t("preview_placeholder"))
        self.last_rendered_code = ""
        self.debug_session.clear_breakpoints()
        self.debug_code_text.clear()
        self._debug_paused_node_id = None
        self._mark_flow_clean()
        self.log("all", "已新建空流程。")
        return True

    def auto_layout_flow(self) -> None:
        try:
            self.graph.auto_layout_nodes()
            self._frame_nodes_in_viewport()
            self.log("all", "已完成自动排版。")
        except RecursionError:
            self.center_flow()
            self.log("all", "当前流程包含循环结构，已跳过自动排版并执行画布居中。")

    def center_flow(self) -> None:
        self._frame_nodes_in_viewport()
        self.log("all", "已将当前 flow 移到画布中心。")

    def _disconnect_node_connections(self, nodes: list[WorkflowNode], mode: str = "all") -> int:
        disconnected = 0
        for current in nodes:
            ports: list[Any] = []
            if mode in {"all", "inputs"}:
                ports.extend(current.inputs().values())
            if mode in {"all", "outputs"}:
                ports.extend(current.outputs().values())
            for port in ports:
                disconnected += len(port.connected_ports())
                port.clear_connections()
        return disconnected

    def arrange_nodes_row(self) -> None:
        nodes = self._target_nodes()
        if not nodes:
            return
        anchor_x = min(node.x_pos() for node in nodes)
        anchor_y = min(node.y_pos() for node in nodes)
        for index, node in enumerate(nodes):
            node.set_pos(anchor_x + index * 240.0, anchor_y)
        self._frame_nodes_in_viewport(nodes)
        self.log("all", f"已按单行排列 {len(nodes)} 个节点。")

    def arrange_nodes_column(self) -> None:
        nodes = self._target_nodes()
        if not nodes:
            return
        anchor_x = min(node.x_pos() for node in nodes)
        anchor_y = min(node.y_pos() for node in nodes)
        for index, node in enumerate(nodes):
            node.set_pos(anchor_x, anchor_y + index * 150.0)
        self._frame_nodes_in_viewport(nodes)
        self.log("all", f"已按单列排列 {len(nodes)} 个节点。")

    def align_nodes_left(self) -> None:
        nodes = self._target_nodes()
        if len(nodes) < 2:
            return
        anchor_x = min(node.x_pos() for node in nodes)
        for node in nodes:
            node.set_pos(anchor_x, node.y_pos())
        self._frame_nodes_in_viewport(nodes)
        self.log("all", f"已左对齐 {len(nodes)} 个节点。")

    def align_nodes_top(self) -> None:
        nodes = self._target_nodes()
        if len(nodes) < 2:
            return
        anchor_y = min(node.y_pos() for node in nodes)
        for node in nodes:
            node.set_pos(node.x_pos(), anchor_y)
        self._frame_nodes_in_viewport(nodes)
        self.log("all", f"已上对齐 {len(nodes)} 个节点。")

    def distribute_nodes_horizontal(self) -> None:
        nodes = sorted(self._target_nodes(), key=lambda node: node.x_pos())
        if len(nodes) < 3:
            return
        start_x = nodes[0].x_pos()
        end_x = nodes[-1].x_pos()
        step = (end_x - start_x) / (len(nodes) - 1)
        for index, node in enumerate(nodes):
            node.set_pos(start_x + step * index, node.y_pos())
        self._frame_nodes_in_viewport(nodes)
        self.log("all", f"已水平分布 {len(nodes)} 个节点。")

    def distribute_nodes_vertical(self) -> None:
        nodes = sorted(self._target_nodes(), key=lambda node: node.y_pos())
        if len(nodes) < 3:
            return
        start_y = nodes[0].y_pos()
        end_y = nodes[-1].y_pos()
        step = (end_y - start_y) / (len(nodes) - 1)
        for index, node in enumerate(nodes):
            node.set_pos(node.x_pos(), start_y + step * index)
        self._frame_nodes_in_viewport(nodes)
        self.log("all", f"已垂直分布 {len(nodes)} 个节点。")

    def disconnect_selected_connections(self) -> None:
        pipes = self.graph.selected_pipes()
        if not pipes:
            self.log("all", "当前未选中连接线。")
            return
        for input_port, output_port in pipes:
            input_port.disconnect_from(output_port)
        self.log("all", f"已断开 {len(pipes)} 条连接线。")

    def build_sample_flow(self, prompt_if_dirty: bool = True) -> bool:
        if not self.new_flow(prompt_if_dirty=prompt_if_dirty):
            return False

        start = self.graph.create_node(StartNode.type_, name="开始")
        comment = self.graph.create_node(CommentNode.type_, name="注释")
        open_session = self.graph.create_node(OpenSignalGeneratorSessionNode.type_, name="打开信号源")
        configure = self.graph.create_node(ConfigureSignalGeneratorWaveformNode.type_, name="配置波形")
        enable_output = self.graph.create_node(SignalGeneratorOutputEnableNode.type_, name="打开输出")
        delay = self.graph.create_node(DelayNode.type_, name="等待稳定")
        query_idn = self.graph.create_node(QuerySignalGeneratorIdentityNode.type_, name="查询标识")
        set_var = self.graph.create_node(SetVariableNode.type_, name="设置变量")
        close_session = self.graph.create_node(CloseSignalGeneratorSessionNode.type_, name="关闭信号源")
        end_node = self.graph.create_node(ReturnNode.type_, name="返回")

        start.set_property("title", "Demo 02 信号发生器流程")
        comment.set_property("message", "这个示例展示顺序执行型的仪器控制 flow。")
        open_session.set_property("session_name", "sg_main")
        open_session.set_property("resource_name", "TCPIP0::192.168.0.10::INSTR")
        configure.set_property("session_name", "sg_main")
        configure.set_property("channel", "CH1")
        configure.set_property("waveform", "SINE")
        configure.set_property("frequency", 1000.0)
        configure.set_property("amplitude", 2.5)
        configure.set_property("offset", 0.1)
        configure.set_property("phase", 0.0)
        enable_output.set_property("session_name", "sg_main")
        enable_output.set_property("channel", "CH1")
        enable_output.set_property("enabled", True)
        delay.set_property("seconds", 0.1)
        query_idn.set_property("session_name", "sg_main")
        query_idn.set_property("save_as", "sg_identity")
        set_var.set_property("variable_name", "flow_tag")
        set_var.set_property("value", "demo_02")
        set_var.set_property("value_type", "str")
        close_session.set_property("session_name", "sg_main")
        end_node.set_property("source_type", "variable")
        end_node.set_property("variable_name", "sg_identity")

        start.set_output(0, comment.input(0))
        comment.set_output(0, open_session.input(0))
        open_session.set_output(0, configure.input(0))
        configure.set_output(0, enable_output.input(0))
        enable_output.set_output(0, delay.input(0))
        delay.set_output(0, query_idn.input(0))
        query_idn.set_output(0, set_var.input(0))
        set_var.set_output(0, close_session.input(0))
        close_session.set_output(0, end_node.input(0))

        self.auto_layout_flow()
        self.current_flow_path = DEFAULT_FLOW_PATH
        self._mark_flow_clean()
        self.log("all", "已生成示例流程。")
        return True

    def _dynamic_node_type(self, module_name: str, class_name: str, method_name: str) -> str:
        from .api_dynamic_nodes import discover_api_method_metas, get_or_create_dynamic_class

        for meta in discover_api_method_metas():
            if meta.module_name.endswith(module_name) and meta.class_name == class_name and meta.method_name == method_name:
                return get_or_create_dynamic_class(meta).type_
        raise KeyError(f"未找到动态节点: {module_name}.{class_name}.{method_name}")

    def build_dynamic_sample_flow(self, prompt_if_dirty: bool = True) -> bool:
        if not self.new_flow(prompt_if_dirty=prompt_if_dirty):
            return False

        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()

        start = self.graph.create_node(StartNode.type_, name="开始")
        set_loop_count = self.graph.create_node(SetVariableNode.type_, name="设置循环次数")
        read_loop_count = self.graph.create_node(ReadIntVariableNode.type_, name="读取循环次数")
        init = self.graph.create_node(
            self._dynamic_node_type("signal_generator", "SimSignalGeneratorIvi", "initialize"),
            name="初始化信号源",
        )
        self_test = self.graph.create_node(
            self._dynamic_node_type("signal_generator", "SimSignalGeneratorIvi", "self_test"),
            name="信号源自检",
        )
        unpack_test = self.graph.create_node(LastResultIndexNode.type_, name="拆包自检信息")
        write_test_message = self.graph.create_node(WriteVariableFromInputNode.type_, name="写回自检信息")
        loop = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "for_range"),
            name="FOR 循环",
        )
        phase_offset = self.graph.create_node(FloatConstantNode.type_, name="相位偏移")
        phase_math = self.graph.create_node(MathBinaryNode.type_, name="相位计算")
        config = self.graph.create_node(
            self._dynamic_node_type("signal_generator", "SimSignalGeneratorIvi", "configure_waveform"),
            name="动态配置波形",
        )
        delay_loop = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "blocking_delay_loop"),
            name="阻塞延时循环",
        )
        query = self.graph.create_node(
            self._dynamic_node_type("signal_generator", "SimSignalGeneratorIvi", "get_identity"),
            name="读取身份",
        )
        write_identity = self.graph.create_node(WriteVariableFromInputNode.type_, name="写回身份变量")
        end_node = self.graph.create_node(ReturnNode.type_, name="返回")

        start.set_property("title", "Demo 02 动态 API 控制流")
        set_loop_count.set_property("variable_name", "loop_count")
        set_loop_count.set_property("value", "3")
        set_loop_count.set_property("value_type", "int")
        read_loop_count.set_property("variable_name", "loop_count")
        read_loop_count.set_property("default_value", 1)
        init.set_property("resource_name", "TCPIP0::192.168.0.10::INSTR")
        init.set_property("id_query", True)
        init.set_property("reset", False)
        unpack_test.set_property("index", 1)
        unpack_test.set_property("default_value", "self_test_missing")
        write_test_message.set_property("variable_name", "self_test_message")
        write_test_message.set_property("fallback_value", "fallback_self_test")
        loop.set_property("value", 1)
        phase_offset.set_property("value", 0.25)
        phase_math.set_property("operator", "add")
        phase_math.set_property("right", 0.0)
        config.set_property("channel", "CH1")
        config.set_property("waveform", "SINE")
        config.set_property("frequency", 1000.0)
        config.set_property("amplitude", 2.0)
        config.set_property("offset", 0.0)
        config.set_property("phase", 0.0)
        delay_loop.set_property("seconds", 0.01)
        delay_loop.set_property("loops", 1)
        write_identity.set_property("variable_name", "sg_identity")
        write_identity.set_property("fallback_value", "")
        end_node.set_property("source_type", "variable")
        end_node.set_property("variable_name", "sg_identity")

        start.flow_output_port().connect_to(set_loop_count.flow_input_port())
        set_loop_count.flow_output_port().connect_to(read_loop_count.flow_input_port())
        read_loop_count.flow_output_port().connect_to(init.flow_input_port())
        init.flow_output_port().connect_to(self_test.flow_input_port())
        self_test.flow_output_port().connect_to(unpack_test.flow_input_port())
        unpack_test.flow_output_port().connect_to(write_test_message.flow_input_port())
        write_test_message.flow_output_port().connect_to(phase_offset.flow_input_port())
        phase_offset.flow_output_port().connect_to(loop.flow_input_port())
        loop.flow_output_port("loop_body").connect_to(phase_math.flow_input_port())
        phase_math.flow_output_port().connect_to(config.flow_input_port())
        config.flow_output_port().connect_to(delay_loop.flow_input_port())
        delay_loop.flow_output_port("flow_out").connect_to(loop.flow_input_port())
        loop.flow_output_port("completed").connect_to(query.flow_input_port())
        query.flow_output_port().connect_to(write_identity.flow_input_port())
        write_identity.flow_output_port().connect_to(end_node.flow_input_port())

        read_loop_count.data_output_port("value").connect_to(loop.data_input_port("value"))
        init.data_output_port("handle").connect_to(self_test.data_input_port("handle"))
        init.data_output_port("handle").connect_to(config.data_input_port("handle"))
        init.data_output_port("handle").connect_to(query.data_input_port("handle"))
        unpack_test.data_output_port("value").connect_to(write_test_message.data_input_port("value"))
        loop.data_output_port("current_value").connect_to(phase_math.data_input_port("left"))
        phase_offset.data_output_port("value").connect_to(phase_math.data_input_port("right"))
        phase_math.data_output_port("result").connect_to(config.data_input_port("phase"))
        query.data_output_port("identity").connect_to(write_identity.data_input_port("value"))

        placements = {
            start: (-520.0, -40.0),
            set_loop_count: (-280.0, -40.0),
            read_loop_count: (-40.0, -40.0),
            init: (220.0, -40.0),
            self_test: (500.0, -40.0),
            unpack_test: (780.0, -40.0),
            write_test_message: (1060.0, -40.0),
            loop: (1340.0, -40.0),
            phase_offset: (1060.0, -220.0),
            phase_math: (1340.0, -220.0),
            config: (1620.0, -220.0),
            delay_loop: (1880.0, -220.0),
            query: (1620.0, 100.0),
            write_identity: (1880.0, 100.0),
            end_node: (2140.0, 100.0),
        }
        for node, (x, y) in placements.items():
            node.set_pos(x, y)
        self.center_flow()
        self.current_flow_path = DEFAULT_FLOW_PATH
        self._mark_flow_clean()
        self.log("all", "已生成动态 API 示例流程。")
        return True

    def build_branch_sample_flow(self, prompt_if_dirty: bool = True) -> bool:
        if not self.new_flow(prompt_if_dirty=prompt_if_dirty):
            return False

        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()

        start = self.graph.create_node(StartNode.type_, name="开始")
        left_number = self.graph.create_node(IntegerConstantNode.type_, name="整数常量-左")
        right_number = self.graph.create_node(IntegerConstantNode.type_, name="整数常量-右")
        compare_number = self.graph.create_node(CompareNumberNode.type_, name="数值比较")
        left_text = self.graph.create_node(TextConstantNode.type_, name="文本常量-左")
        right_text = self.graph.create_node(TextConstantNode.type_, name="文本常量-右")
        compare_text = self.graph.create_node(CompareTextNode.type_, name="文本比较")
        bool_logic = self.graph.create_node(BooleanLogicNode.type_, name="布尔逻辑")
        bool_source = self.graph.create_node(BooleanConstantNode.type_, name="布尔常量")
        bool_not = self.graph.create_node(BooleanNotNode.type_, name="布尔非")
        if_node = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "if_branch"),
            name="IF 分支",
        )
        elif_node = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "elif_branch"),
            name="ELIF 分支",
        )
        else_node = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "else_branch"),
            name="ELSE 分支",
        )
        terminate_true = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "terminate_flow"),
            name="终止-IF",
        )
        terminate_elif = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "terminate_flow"),
            name="终止-ELIF",
        )
        terminate_skip = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "terminate_flow"),
            name="终止-SKIP",
        )
        end_node = self.graph.create_node(ReturnNode.type_, name="返回")

        start.set_property("title", "Demo 02 分支控制流")
        left_number.set_property("value", 1)
        right_number.set_property("value", 2)
        compare_number.set_property("operator", "gt")
        left_text.set_property("value", "alpha")
        right_text.set_property("value", "z")
        compare_text.set_property("operator", "contains")
        bool_logic.set_property("operator", "or")
        bool_source.set_property("value", True)
        if_node.set_property("condition", False)
        if_node.set_property("true_value", "if_path")
        if_node.set_property("false_value", "fallthrough")
        elif_node.set_property("condition", False)
        elif_node.set_property("value", "elif_path")
        else_node.set_property("value", "else_path")
        terminate_true.set_property("message", "if branch terminated")
        terminate_elif.set_property("message", "elif branch terminated")
        terminate_skip.set_property("message", "else skipped")
        end_node.set_property("source_type", "last_result")

        start.flow_output_port().connect_to(left_number.flow_input_port())
        left_number.flow_output_port().connect_to(right_number.flow_input_port())
        right_number.flow_output_port().connect_to(compare_number.flow_input_port())
        compare_number.flow_output_port().connect_to(left_text.flow_input_port())
        left_text.flow_output_port().connect_to(right_text.flow_input_port())
        right_text.flow_output_port().connect_to(compare_text.flow_input_port())
        compare_text.flow_output_port().connect_to(bool_logic.flow_input_port())
        bool_logic.flow_output_port().connect_to(bool_source.flow_input_port())
        bool_source.flow_output_port().connect_to(bool_not.flow_input_port())
        bool_not.flow_output_port().connect_to(if_node.flow_input_port())
        if_node.flow_output_port("true_branch").connect_to(terminate_true.flow_input_port())
        if_node.flow_output_port("false_branch").connect_to(elif_node.flow_input_port())
        elif_node.flow_output_port("true_branch").connect_to(terminate_elif.flow_input_port())
        elif_node.flow_output_port("false_branch").connect_to(else_node.flow_input_port())
        else_node.flow_output_port("else_branch").connect_to(end_node.flow_input_port())
        else_node.flow_output_port("skipped").connect_to(terminate_skip.flow_input_port())

        left_number.data_output_port("value").connect_to(compare_number.data_input_port("left"))
        right_number.data_output_port("value").connect_to(compare_number.data_input_port("right"))
        left_text.data_output_port("value").connect_to(compare_text.data_input_port("left"))
        right_text.data_output_port("value").connect_to(compare_text.data_input_port("right"))
        compare_number.data_output_port("result").connect_to(bool_logic.data_input_port("left"))
        compare_text.data_output_port("result").connect_to(bool_logic.data_input_port("right"))
        bool_logic.data_output_port("result").connect_to(if_node.data_input_port("condition"))
        bool_source.data_output_port("value").connect_to(bool_not.data_input_port("value"))
        bool_not.data_output_port("result").connect_to(elif_node.data_input_port("condition"))
        if_node.data_output_port("matched").connect_to(elif_node.data_input_port("previous_matched"))
        elif_node.data_output_port("matched").connect_to(else_node.data_input_port("previous_matched"))

        placements = {
            start: (-520.0, -40.0),
            left_number: (-300.0, -220.0),
            right_number: (-40.0, -220.0),
            compare_number: (220.0, -220.0),
            left_text: (-300.0, 0.0),
            right_text: (-40.0, 0.0),
            compare_text: (220.0, 0.0),
            bool_logic: (500.0, -120.0),
            bool_source: (500.0, 80.0),
            bool_not: (760.0, 80.0),
            if_node: (760.0, -160.0),
            elif_node: (1030.0, -20.0),
            else_node: (1300.0, 120.0),
            terminate_true: (1030.0, -220.0),
            terminate_elif: (1300.0, -20.0),
            terminate_skip: (1570.0, -20.0),
            end_node: (1570.0, 120.0),
        }
        for node, (x, y) in placements.items():
            node.set_pos(x, y)
        self.center_flow()
        self.current_flow_path = DEFAULT_FLOW_PATH
        self._mark_flow_clean()
        self.log("all", "已生成分支控制流示例。")
        return True

    def build_while_sample_flow(self, prompt_if_dirty: bool = True) -> bool:
        if not self.new_flow(prompt_if_dirty=prompt_if_dirty):
            return False

        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()

        start = self.graph.create_node(StartNode.type_, name="开始")
        bool_source = self.graph.create_node(BooleanConstantNode.type_, name="布尔常量")
        max_iterations = self.graph.create_node(IntegerConstantNode.type_, name="最大迭代")
        while_node = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "while_loop"),
            name="WHILE 循环",
        )
        delay_loop = self.graph.create_node(
            self._dynamic_node_type("general", "GeneralFlowApi", "blocking_delay_loop"),
            name="阻塞延时循环",
        )
        end_node = self.graph.create_node(ReturnNode.type_, name="返回")

        start.set_property("title", "Demo 02 While 控制流")
        bool_source.set_property("value", True)
        max_iterations.set_property("value", 2)
        while_node.set_property("condition", True)
        while_node.set_property("max_iterations", 1)
        delay_loop.set_property("seconds", 0.01)
        delay_loop.set_property("loops", 1)
        end_node.set_property("source_type", "last_result")

        start.flow_output_port().connect_to(bool_source.flow_input_port())
        bool_source.flow_output_port().connect_to(max_iterations.flow_input_port())
        max_iterations.flow_output_port().connect_to(while_node.flow_input_port())
        while_node.flow_output_port("loop_body").connect_to(delay_loop.flow_input_port())
        delay_loop.flow_output_port("flow_out").connect_to(while_node.flow_input_port())
        while_node.flow_output_port("completed").connect_to(end_node.flow_input_port())

        bool_source.data_output_port("value").connect_to(while_node.data_input_port("condition"))
        max_iterations.data_output_port("value").connect_to(while_node.data_input_port("max_iterations"))

        placements = {
            start: (-540.0, -40.0),
            bool_source: (-300.0, -160.0),
            max_iterations: (-300.0, 80.0),
            while_node: (-20.0, -40.0),
            delay_loop: (260.0, -160.0),
            end_node: (260.0, 100.0),
        }
        for node, (x, y) in placements.items():
            node.set_pos(x, y)
        self.center_flow()
        self.current_flow_path = DEFAULT_FLOW_PATH
        self._mark_flow_clean()
        self.log("all", "已生成 WHILE 控制流示例。")
        return True

    def build_digital_pattern_sample_flow(self, prompt_if_dirty: bool = True) -> bool:
        if not self.new_flow(prompt_if_dirty=prompt_if_dirty):
            return False

        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()

        start = self.graph.create_node(StartNode.type_, name="开始")
        init = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "initialize"),
            name="初始化数字模式发生器",
        )
        self_test = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "self_test"),
            name="数字模式自检",
        )
        unpack_test = self.graph.create_node(LastResultIndexNode.type_, name="拆包自检消息")
        write_test = self.graph.create_node(WriteVariableFromInputNode.type_, name="写回自检消息")
        configure_timing = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "configure_timing"),
            name="配置时序",
        )
        load_pattern = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "load_pattern"),
            name="加载模式",
        )
        start_output = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "start_output"),
            name="开始输出",
        )
        query_status = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "query_status"),
            name="查询状态",
        )
        write_timing = self.graph.create_node(WriteVariableFromInputNode.type_, name="写回时序摘要")
        stop_output = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "stop_output"),
            name="停止输出",
        )
        close_session = self.graph.create_node(
            self._dynamic_node_type("digital_pattern_generator", "SimDigitalPatternGeneratorIvi", "close"),
            name="关闭数字模式会话",
        )
        end_node = self.graph.create_node(ReturnNode.type_, name="返回")

        start.set_property("title", "Demo 02 数字模式发生器动态流程")
        init.set_property("resource_name", "PXI0::20-0.0::INSTR")
        init.set_property("id_query", True)
        init.set_property("reset", False)
        unpack_test.set_property("index", 1)
        unpack_test.set_property("default_value", "dpg_self_test_missing")
        write_test.set_property("variable_name", "dpg_self_test")
        configure_timing.set_property("sample_rate", 1_000_000.0)
        configure_timing.set_property("logic_level", "3.3V")
        load_pattern.set_property("pattern_name", "burst_A")
        load_pattern.set_property("pattern_bits", "101100111000")
        load_pattern.set_property("loop_count", 2)
        write_timing.set_property("variable_name", "dpg_timing")
        stop_output.set_property("save_prefix", "stop_output")
        close_session.set_property("save_prefix", "close_session")
        end_node.set_property("source_type", "variable")
        end_node.set_property("variable_name", "dpg_timing")

        start.flow_output_port().connect_to(init.flow_input_port())
        init.flow_output_port().connect_to(self_test.flow_input_port())
        self_test.flow_output_port().connect_to(unpack_test.flow_input_port())
        unpack_test.flow_output_port().connect_to(write_test.flow_input_port())
        write_test.flow_output_port().connect_to(configure_timing.flow_input_port())
        configure_timing.flow_output_port().connect_to(load_pattern.flow_input_port())
        load_pattern.flow_output_port().connect_to(start_output.flow_input_port())
        start_output.flow_output_port().connect_to(query_status.flow_input_port())
        query_status.flow_output_port().connect_to(write_timing.flow_input_port())
        write_timing.flow_output_port().connect_to(stop_output.flow_input_port())
        stop_output.flow_output_port().connect_to(close_session.flow_input_port())
        close_session.flow_output_port().connect_to(end_node.flow_input_port())

        init.data_output_port("handle").connect_to(self_test.data_input_port("handle"))
        init.data_output_port("handle").connect_to(configure_timing.data_input_port("handle"))
        init.data_output_port("handle").connect_to(load_pattern.data_input_port("handle"))
        init.data_output_port("handle").connect_to(start_output.data_input_port("handle"))
        init.data_output_port("handle").connect_to(query_status.data_input_port("handle"))
        init.data_output_port("handle").connect_to(stop_output.data_input_port("handle"))
        init.data_output_port("handle").connect_to(close_session.data_input_port("handle"))
        unpack_test.data_output_port("value").connect_to(write_test.data_input_port("value"))
        query_status.data_output_port("timing").connect_to(write_timing.data_input_port("value"))

        placements = {
            start: (-520.0, -40.0),
            init: (-260.0, -40.0),
            self_test: (0.0, -40.0),
            unpack_test: (260.0, -40.0),
            write_test: (520.0, -40.0),
            configure_timing: (780.0, -160.0),
            load_pattern: (1040.0, -160.0),
            start_output: (1300.0, -160.0),
            query_status: (1560.0, -40.0),
            write_timing: (1820.0, -40.0),
            stop_output: (2080.0, -40.0),
            close_session: (2340.0, -40.0),
            end_node: (2600.0, -40.0),
        }
        for node, (x, y) in placements.items():
            node.set_pos(x, y)
        self.center_flow()
        self.current_flow_path = DEFAULT_FLOW_PATH
        self._mark_flow_clean()
        self.log("all", "已生成数字模式发生器动态示例。")
        return True

    def build_serial_sample_flow(self, prompt_if_dirty: bool = True) -> bool:
        if not self.new_flow(prompt_if_dirty=prompt_if_dirty):
            return False

        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()

        start = self.graph.create_node(StartNode.type_, name="开始")
        init = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "initialize"),
            name="初始化串口卡",
        )
        self_test = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "self_test"),
            name="串口卡自检",
        )
        unpack_test = self.graph.create_node(LastResultIndexNode.type_, name="拆包串口自检")
        write_test = self.graph.create_node(WriteVariableFromInputNode.type_, name="写回串口自检")
        payload_text = self.graph.create_node(TextConstantNode.type_, name="串口发送文本")
        open_port = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "open_port"),
            name="打开端口",
        )
        write_serial = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "write"),
            name="写串口",
        )
        read_serial = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "read"),
            name="读串口",
        )
        write_reply = self.graph.create_node(WriteVariableFromInputNode.type_, name="写回串口回复")
        close_port = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "close_port"),
            name="关闭端口",
        )
        close_session = self.graph.create_node(
            self._dynamic_node_type("multi_serial_card", "SimMultiSerialCardIvi", "close"),
            name="关闭串口会话",
        )
        end_node = self.graph.create_node(ReturnNode.type_, name="返回")

        start.set_property("title", "Demo 02 串口卡动态流程")
        init.set_property("resource_name", "PCI::SERIAL-CARD-01")
        init.set_property("id_query", True)
        init.set_property("reset", False)
        unpack_test.set_property("index", 1)
        unpack_test.set_property("default_value", "serial_self_test_missing")
        write_test.set_property("variable_name", "serial_self_test")
        payload_text.set_property("value", "*IDN?")
        open_port.set_property("channel", "CH1")
        open_port.set_property("port_name", "COM1")
        open_port.set_property("baud_rate", 115200)
        open_port.set_property("data_bits", 8)
        open_port.set_property("parity", "N")
        open_port.set_property("stop_bits", 1)
        open_port.set_property("timeout", 1.0)
        write_serial.set_property("channel", "CH1")
        write_serial.set_property("encoding", "utf-8")
        read_serial.set_property("channel", "CH1")
        read_serial.set_property("size", 0)
        read_serial.set_property("timeout", 1.0)
        write_reply.set_property("variable_name", "serial_reply")
        close_port.set_property("channel", "CH1")
        end_node.set_property("source_type", "variable")
        end_node.set_property("variable_name", "serial_reply")

        start.flow_output_port().connect_to(init.flow_input_port())
        init.flow_output_port().connect_to(self_test.flow_input_port())
        self_test.flow_output_port().connect_to(unpack_test.flow_input_port())
        unpack_test.flow_output_port().connect_to(write_test.flow_input_port())
        write_test.flow_output_port().connect_to(payload_text.flow_input_port())
        payload_text.flow_output_port().connect_to(open_port.flow_input_port())
        open_port.flow_output_port().connect_to(write_serial.flow_input_port())
        write_serial.flow_output_port().connect_to(read_serial.flow_input_port())
        read_serial.flow_output_port().connect_to(write_reply.flow_input_port())
        write_reply.flow_output_port().connect_to(close_port.flow_input_port())
        close_port.flow_output_port().connect_to(close_session.flow_input_port())
        close_session.flow_output_port().connect_to(end_node.flow_input_port())

        init.data_output_port("handle").connect_to(self_test.data_input_port("handle"))
        init.data_output_port("handle").connect_to(open_port.data_input_port("handle"))
        init.data_output_port("handle").connect_to(write_serial.data_input_port("handle"))
        init.data_output_port("handle").connect_to(read_serial.data_input_port("handle"))
        init.data_output_port("handle").connect_to(close_port.data_input_port("handle"))
        init.data_output_port("handle").connect_to(close_session.data_input_port("handle"))
        unpack_test.data_output_port("value").connect_to(write_test.data_input_port("value"))
        payload_text.data_output_port("value").connect_to(write_serial.data_input_port("data"))
        read_serial.data_output_port("reply").connect_to(write_reply.data_input_port("value"))

        placements = {
            start: (-520.0, -40.0),
            init: (-260.0, -40.0),
            self_test: (0.0, -40.0),
            unpack_test: (260.0, -40.0),
            write_test: (520.0, -40.0),
            payload_text: (780.0, -40.0),
            open_port: (1040.0, -160.0),
            write_serial: (1300.0, -160.0),
            read_serial: (1560.0, -160.0),
            write_reply: (1820.0, -40.0),
            close_port: (2080.0, -40.0),
            close_session: (2340.0, -40.0),
            end_node: (2600.0, -40.0),
        }
        for node, (x, y) in placements.items():
            node.set_pos(x, y)
        self.center_flow()
        self.current_flow_path = DEFAULT_FLOW_PATH
        self._mark_flow_clean()
        self.log("all", "已生成串口卡动态示例。")
        return True

    def _save_flow_to(self, path: Path) -> Path:
        path = ensure_parent_directory(path)
        self.graph.save_session(str(path))
        self.current_flow_path = path
        self._mark_flow_clean()
        self.log("all", f"流程已保存: {path}")
        return path

    def save_flow(self) -> Path | None:
        target = self.current_flow_path or DEFAULT_FLOW_PATH
        return self._save_flow_to(target)

    def save_flow_as(self) -> Path | None:
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.t("save_flow_as"),
            str(self.current_flow_path or DEFAULT_FLOW_PATH),
            "JSON Files (*.json)",
        )
        if not file_path:
            return None
        return self._save_flow_to(Path(file_path))

    def open_flow(self) -> Path | None:
        if not self._confirm_can_abandon_current_flow():
            return None
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.t("open_flow"),
            str(self.current_flow_path or DEFAULT_FLOW_PATH),
            "JSON Files (*.json)",
        )
        if not file_path:
            return None
        return self.load_flow_from_path(Path(file_path))

    def load_instrument_api_nodes(self) -> None:
        new_count, discovered = ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()
        self.log(
            "all",
            f"仪器 API：本次新注册 {new_count} 个节点类型，元数据方法 {discovered} 个（支持磁盘缓存与进程内缓存加速扫描），资源树 API 模板 {api_node_template_count()} 个。",
        )

    def load_flow_from_path(self, path: Path) -> Path:
        ensure_instrument_api_registered(self.graph)
        self.resource_tree.rebuild()
        self.debug_session.clear_breakpoints()
        self.debug_code_text.clear()
        self._debug_paused_node_id = None
        self.graph.load_session(str(path))
        configure_graph_port_constraints(self.graph)
        self._refresh_node_visuals()
        self.current_flow_path = path
        self.current_selected_node = None
        self.property_editor.set_node(None)
        self.node_runtime_states.clear()
        self.update_runtime_panel()
        self._mark_flow_clean()
        self.log("all", f"已加载流程: {path}")
        return path

    def validate_flow(self) -> bool:
        validator = WorkflowValidator(self.graph)
        messages, _analysis = validator.validate()
        content = "\n".join(f"[{msg.level.upper()}] {msg.message}" for msg in messages)
        self.validation_text.setPlainText(content)
        for message in messages:
            self.log("validate", message.message)
        if not validator.has_errors(messages):
            self.render_code_preview()
        return not validator.has_errors(messages)

    def render_code_preview(self) -> str:
        code = WorkflowExporter(self.graph).render_code()
        self.last_rendered_code = code
        self.preview_text.setPlainText(code)
        return code

    def preview_code(self) -> None:
        if not self.validate_flow():
            self.log("export", "源码预览中止：流程校验未通过。")
            return
        code = self.last_rendered_code
        if not code:
            try:
                code = self.render_code_preview()
            except Exception as exc:
                self.log("export", f"源码预览失败: {exc}")
                return
        self.preview_dialog.set_title(self.t("preview_dialog"))
        self.preview_dialog.set_close_text(self.t("close"))
        self.preview_dialog.set_code(code)
        self.preview_dialog.exec()

    def export_python(self, target_path: Path | None = None) -> Path | None:
        if not self.validate_flow():
            self.log("export", "导出中止：流程校验未通过。")
            return None
        exporter = WorkflowExporter(self.graph)
        if target_path is None:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                self.t("export_python"),
                str(DEFAULT_EXPORT_PATH),
                "Python Files (*.py)",
            )
            if not file_path:
                return None
            target_path = Path(file_path)
        target_path = ensure_parent_directory(target_path)
        exporter.export_to_file(target_path)
        self.last_rendered_code = exporter.render_code()
        self.preview_text.setPlainText(self.last_rendered_code)
        self.log("export", f"已导出 Python: {target_path}")
        return target_path

    def run_flow(self) -> None:
        if self._run_controller is not None and self._run_controller.is_running():
            self.log("run", "已有流程在子进程中运行，请等待结束或使用「停止流程」。")
            return
        if self._debug_worker is not None and self._debug_worker.isRunning():
            self.log("run", "请先停止调试再运行流程。")
            return
        if not self.validate_flow():
            self.log("run", "运行中止：流程校验未通过。")
            return
        self.node_runtime_states.clear()
        self._reset_runtime_visuals()
        ensure_directory(GENERATED_DIR)
        fd, tmp_name = tempfile.mkstemp(suffix=".json", dir=str(GENERATED_DIR))
        os.close(fd)
        path = Path(tmp_name)
        self.graph.save_session(str(path))
        self._run_temp_json = path
        ctrl = FlowRunController(self)
        ctrl.logEmitted.connect(self.log, QtCore.Qt.QueuedConnection)
        ctrl.finishedRun.connect(self._on_subprocess_run_finished)
        self._run_controller = ctrl
        self._update_execution_action_states()
        self.log("run", f"[子进程] 启动运行（不阻塞界面）: {path.name}")
        ctrl.start_run(path, self.current_language)

    def _on_subprocess_run_finished(self, ok: bool, message: str) -> None:
        if self._run_temp_json is not None and self._run_temp_json.is_file():
            try:
                self._run_temp_json.unlink()
            except OSError:
                pass
        self._run_temp_json = None
        if self._run_controller is not None:
            self._run_controller.deleteLater()
            self._run_controller = None
        self._update_execution_action_states()
        suffix = "成功" if ok else "失败"
        self.log("run", f"[子进程] {message} — {suffix}")
        self.statusBar().showMessage(f"{message} ({suffix})", 5000)

    def stop_flow(self) -> None:
        if self._run_controller is not None and self._run_controller.is_running():
            self._run_controller.stop()
            self.log("run", "已请求终止子进程中的流程运行。")
            return
        if self._debug_worker is not None and self._debug_worker.isRunning():
            self.debug_session.stop()
            self.log("run", "已请求停止调试会话。")
            return
        self.log("run", self.t("runtime_not_supported"))

    def _restore_main_layout_from_settings(self) -> None:
        self._layout_store.restore(
            self._main_h_splitter,
            self._main_v_splitter,
            self.right_panel,
            self.log_tabs,
        )

    def _save_main_layout_to_settings(self) -> None:
        self._layout_store.save(
            self._main_h_splitter,
            self._main_v_splitter,
            self.right_panel,
            self.log_tabs,
        )

    def showEvent(self, event: QtGui.QShowEvent) -> None:  # type: ignore[override]
        super().showEvent(event)
        if not self._layout_restored:
            self._restore_main_layout_from_settings()
            self._layout_restored = True

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # type: ignore[override]
        if self._run_controller is not None and self._run_controller.is_running():
            self._run_controller.stop()
        if self._confirm_can_abandon_current_flow():
            self._save_main_layout_to_settings()
            event.accept()
            return
        event.ignore()

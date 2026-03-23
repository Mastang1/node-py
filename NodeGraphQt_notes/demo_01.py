from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

HEADLESS_SMOKE_FLAG = "--headless-smoke-test"
if HEADLESS_SMOKE_FLAG in sys.argv:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = BASE_DIR.parent
NODEGRAPHQT_ROOT = WORKSPACE_ROOT / "NodeGraphQt"
if str(NODEGRAPHQT_ROOT) not in sys.path:
    sys.path.insert(0, str(NODEGRAPHQT_ROOT))

from Qt import QtCore, QtWidgets

from NodeGraphQt import BaseNode, NodeGraph, NodesPaletteWidget, NodesTreeWidget, PropertiesBinWidget
from NodeGraphQt.constants import LayoutDirectionEnum
from NodeGraphQt.nodes.backdrop_node import BackdropNode

FLOW_IN = "flow_in"
FLOW_OUT = "flow_out"
DEFAULT_CHANNELS = ("CH1", "CH2")
GENERATED_DIR = BASE_DIR / "generated"
DEFAULT_GRAPH_PATH = GENERATED_DIR / "demo_01_graph.json"
DEFAULT_EXPORT_PATH = GENERATED_DIR / "demo_01_exported_workflow.py"

EXPORTED_API_SOURCE = """
class VirtualInstrumentAPI:
    def __init__(self):
        self.resource_name = None
        self.is_open = False
        self.channels = {
            "CH1": {"enabled": False, "voltage": 0.0},
            "CH2": {"enabled": False, "voltage": 0.0},
        }

    def _ensure_open(self):
        if not self.is_open:
            raise RuntimeError("Instrument session is not open.")

    def _get_channel(self, channel):
        channel_name = str(channel).strip().upper()
        if channel_name not in self.channels:
            raise RuntimeError(f"Unknown channel: {channel_name}")
        return channel_name, self.channels[channel_name]

    def open(self, resource_name):
        self.resource_name = str(resource_name).strip()
        self.is_open = True
        print(f"[API] open -> {self.resource_name}")

    def enable_output(self, channel, enabled):
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        state["enabled"] = bool(enabled)
        print(f"[API] output {channel_name} -> {state['enabled']}")

    def set_voltage(self, channel, voltage):
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        state["voltage"] = float(voltage)
        print(f"[API] set voltage {channel_name} -> {state['voltage']:.3f} V")

    def measure_voltage(self, channel):
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        value = round(state["voltage"] + (0.002 if state["enabled"] else 0.0), 4)
        print(f"[API] measure {channel_name} -> {value:.4f} V")
        return value

    def close(self):
        if not self.is_open:
            print("[API] close skipped - already closed")
            return
        print(f"[API] close -> {self.resource_name}")
        self.is_open = False
        self.resource_name = None
""".strip()


class WorkflowError(RuntimeError):
    pass


def ensure_parent_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def as_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def as_float(value: object, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def as_bool(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def sanitize_identifier(value: object, default: str = "result") -> str:
    text = as_text(value, default)
    cleaned = []
    for char in text:
        if char.isalnum() or char == "_":
            cleaned.append(char)
        else:
            cleaned.append("_")
    result = "".join(cleaned).strip("_")
    if not result:
        result = default
    if result[0].isdigit():
        result = f"var_{result}"
    return result


def node_sort_key(node: BaseNode) -> tuple[float, float, str, str]:
    return (round(node.y_pos(), 3), round(node.x_pos(), 3), node.name(), node.id)


class VirtualInstrumentAPI:
    def __init__(self, logger: Callable[[str], None] | None = None, sleep_scale: float = 1.0):
        self._logger = logger or print
        self._sleep_scale = sleep_scale
        self.resource_name: str | None = None
        self.is_open = False
        self.channels = {
            channel: {"enabled": False, "voltage": 0.0}
            for channel in DEFAULT_CHANNELS
        }

    def _log(self, message: str) -> None:
        self._logger(f"[API] {message}")

    def _ensure_open(self) -> None:
        if not self.is_open:
            raise WorkflowError("Instrument session is not open.")

    def _get_channel(self, channel: str) -> tuple[str, dict[str, object]]:
        channel_name = as_text(channel, DEFAULT_CHANNELS[0]).upper()
        if channel_name not in self.channels:
            raise WorkflowError(f"Unknown channel: {channel_name}")
        return channel_name, self.channels[channel_name]

    def open(self, resource_name: str) -> None:
        self.resource_name = as_text(resource_name, "SIM::INSTR")
        self.is_open = True
        self._log(f"open -> {self.resource_name}")

    def enable_output(self, channel: str, enabled: bool) -> None:
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        state["enabled"] = bool(enabled)
        self._log(f"output {channel_name} -> {state['enabled']}")

    def set_voltage(self, channel: str, voltage: float) -> None:
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        state["voltage"] = float(voltage)
        self._log(f"set voltage {channel_name} -> {state['voltage']:.3f} V")

    def measure_voltage(self, channel: str) -> float:
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        value = round(float(state["voltage"]) + (0.002 if state["enabled"] else 0.0), 4)
        self._log(f"measure {channel_name} -> {value:.4f} V")
        return value

    def delay(self, seconds: float) -> None:
        wait_seconds = max(0.0, float(seconds))
        self._log(f"delay -> {wait_seconds:.3f} s")
        scaled = wait_seconds * self._sleep_scale
        if scaled > 0.0:
            time.sleep(scaled)

    def close(self) -> None:
        if not self.is_open:
            self._log("close skipped - already closed")
            return
        self._log(f"close -> {self.resource_name}")
        self.is_open = False
        self.resource_name = None


@dataclass
class RuntimeState:
    logger: Callable[[str], None]
    sleep_scale: float = 1.0
    api: VirtualInstrumentAPI | None = None
    values: dict[str, object] = field(default_factory=dict)

    def log(self, message: str) -> None:
        self.logger(message)

    def require_api(self, node_name: str) -> VirtualInstrumentAPI:
        if self.api is None or not self.api.is_open:
            raise WorkflowError(
                f'{node_name} requires an open instrument session. '
                "Place Open Instrument before control nodes."
            )
        return self.api


class InstrumentFlowNode(BaseNode):
    __identifier__ = "demo.instrument"
    NODE_COLOR = (56, 80, 132)
    FLOW_IN_COLOR = (237, 177, 82)
    FLOW_OUT_COLOR = (77, 191, 162)

    def __init__(self, has_flow_input: bool = True, has_flow_output: bool = True):
        super().__init__()
        self.set_color(*self.NODE_COLOR)
        if has_flow_input:
            self.add_input(FLOW_IN, multi_input=False, color=self.FLOW_IN_COLOR)
        if has_flow_output:
            self.add_output(FLOW_OUT, multi_output=True, color=self.FLOW_OUT_COLOR)

    def flow_sources(self) -> list["InstrumentFlowNode"]:
        port = self.inputs().get(FLOW_IN)
        if not port:
            return []
        return [source.node() for source in port.connected_ports() if isinstance(source.node(), InstrumentFlowNode)]

    def flow_targets(self) -> list["InstrumentFlowNode"]:
        port = self.outputs().get(FLOW_OUT)
        if not port:
            return []
        return [target.node() for target in port.connected_ports() if isinstance(target.node(), InstrumentFlowNode)]

    def python_api_guard(self) -> list[str]:
        message = (
            f"{self.name()} requires an open instrument session. "
            "Add Open Instrument before this node."
        )
        return [
            "if api is None or not api.is_open:",
            f"    raise RuntimeError({message!r})",
        ]

    def execute(self, state: RuntimeState) -> None:
        raise NotImplementedError

    def emit_python(self) -> list[str]:
        raise NotImplementedError


class StartNode(InstrumentFlowNode):
    NODE_NAME = "Start"
    NODE_COLOR = (44, 108, 74)

    def __init__(self):
        super().__init__(has_flow_input=False, has_flow_output=True)
        self.add_text_input("plan_name", "Plan", "Instrument workflow")

    def execute(self, state: RuntimeState) -> None:
        plan_name = as_text(self.get_property("plan_name"), self.name())
        state.log(f"[Start] {plan_name}")

    def emit_python(self) -> list[str]:
        plan_name = as_text(self.get_property("plan_name"), self.name())
        return [f"print({f'[Start] {plan_name}'!r})"]


class OpenInstrumentNode(InstrumentFlowNode):
    NODE_NAME = "Open Instrument"
    NODE_COLOR = (48, 92, 126)

    def __init__(self):
        super().__init__()
        self.add_text_input("resource_name", "Resource", "TCPIP0::192.168.0.8::INSTR")

    def execute(self, state: RuntimeState) -> None:
        resource_name = as_text(self.get_property("resource_name"), "SIM::INSTR")
        state.api = VirtualInstrumentAPI(logger=state.log, sleep_scale=state.sleep_scale)
        state.api.open(resource_name)
        state.values["resource_name"] = resource_name

    def emit_python(self) -> list[str]:
        resource_name = as_text(self.get_property("resource_name"), "SIM::INSTR")
        return [
            "api = VirtualInstrumentAPI()",
            "context['api'] = api",
            f"api.open({resource_name!r})",
        ]


class SetOutputNode(InstrumentFlowNode):
    NODE_NAME = "Set Output"
    NODE_COLOR = (94, 76, 156)

    def __init__(self):
        super().__init__()
        self.add_combo_menu("channel", "Channel", list(DEFAULT_CHANNELS))
        self.add_checkbox("enabled", "Enabled", "Output On", True)

    def execute(self, state: RuntimeState) -> None:
        api = state.require_api(self.name())
        channel = as_text(self.get_property("channel"), DEFAULT_CHANNELS[0])
        enabled = as_bool(self.get_property("enabled"))
        api.enable_output(channel, enabled)
        state.values[f"{channel}_enabled"] = enabled

    def emit_python(self) -> list[str]:
        channel = as_text(self.get_property("channel"), DEFAULT_CHANNELS[0])
        enabled = as_bool(self.get_property("enabled"))
        return self.python_api_guard() + [f"api.enable_output({channel!r}, {enabled})"]


class SetVoltageNode(InstrumentFlowNode):
    NODE_NAME = "Set Voltage"
    NODE_COLOR = (112, 100, 46)

    def __init__(self):
        super().__init__()
        self.add_combo_menu("channel", "Channel", list(DEFAULT_CHANNELS))
        self.add_text_input("voltage", "Voltage", "5.0")

    def execute(self, state: RuntimeState) -> None:
        api = state.require_api(self.name())
        channel = as_text(self.get_property("channel"), DEFAULT_CHANNELS[0])
        voltage = as_float(self.get_property("voltage"), 0.0)
        api.set_voltage(channel, voltage)
        state.values[f"{channel}_set_voltage"] = voltage

    def emit_python(self) -> list[str]:
        channel = as_text(self.get_property("channel"), DEFAULT_CHANNELS[0])
        voltage = as_float(self.get_property("voltage"), 0.0)
        return self.python_api_guard() + [f"api.set_voltage({channel!r}, {voltage})"]


class DelayNode(InstrumentFlowNode):
    NODE_NAME = "Delay"
    NODE_COLOR = (112, 68, 48)

    def __init__(self):
        super().__init__()
        self.add_text_input("seconds", "Seconds", "0.2")

    def execute(self, state: RuntimeState) -> None:
        seconds = as_float(self.get_property("seconds"), 0.0)
        state.log(f"[Delay] {seconds:.3f} s")
        scaled = max(0.0, seconds) * state.sleep_scale
        if scaled > 0.0:
            time.sleep(scaled)

    def emit_python(self) -> list[str]:
        seconds = as_float(self.get_property("seconds"), 0.0)
        return [
            f"print({f'[Delay] {seconds:.3f} s'!r})",
            f"time.sleep({seconds})",
        ]


class MeasureVoltageNode(InstrumentFlowNode):
    NODE_NAME = "Measure Voltage"
    NODE_COLOR = (44, 120, 124)

    def __init__(self):
        super().__init__()
        self.add_combo_menu("channel", "Channel", list(DEFAULT_CHANNELS))
        self.add_text_input("save_as", "Save As", "measured_voltage")

    def execute(self, state: RuntimeState) -> None:
        api = state.require_api(self.name())
        channel = as_text(self.get_property("channel"), DEFAULT_CHANNELS[0])
        key = sanitize_identifier(self.get_property("save_as"), "measured_voltage")
        value = api.measure_voltage(channel)
        state.values[key] = value
        state.log(f"[Store] {key} = {value}")

    def emit_python(self) -> list[str]:
        channel = as_text(self.get_property("channel"), DEFAULT_CHANNELS[0])
        key = sanitize_identifier(self.get_property("save_as"), "measured_voltage")
        return self.python_api_guard() + [
            f"context[{key!r}] = api.measure_voltage({channel!r})",
            f"print({'[Store] ' + key + ' ='!r}, context[{key!r}])",
        ]


class PrintContextNode(InstrumentFlowNode):
    NODE_NAME = "Print Context"
    NODE_COLOR = (68, 68, 78)

    def __init__(self):
        super().__init__()
        self.add_text_input("message", "Message", "Measured value")
        self.add_text_input("context_key", "Context Key", "measured_voltage")

    def execute(self, state: RuntimeState) -> None:
        message = as_text(self.get_property("message"), "Value")
        key = as_text(self.get_property("context_key"))
        if key:
            value = state.values.get(sanitize_identifier(key, key), "<missing>")
            state.log(f"[Print] {message}: {value}")
            return
        state.log(f"[Print] {message}")

    def emit_python(self) -> list[str]:
        message = as_text(self.get_property("message"), "Value")
        key = as_text(self.get_property("context_key"))
        if key:
            key = sanitize_identifier(key, key)
            return [
                f"print({(message + ':')!r}, context.get({key!r}, '<missing>'))",
            ]
        return [f"print({message!r})"]


class CloseInstrumentNode(InstrumentFlowNode):
    NODE_NAME = "Close Instrument"
    NODE_COLOR = (126, 54, 58)

    def __init__(self):
        super().__init__(has_flow_input=True, has_flow_output=False)

    def execute(self, state: RuntimeState) -> None:
        if state.api and state.api.is_open:
            state.api.close()
            return
        state.log("[Close] skipped - no open session")

    def emit_python(self) -> list[str]:
        return [
            "if api is not None and api.is_open:",
            "    api.close()",
            "else:",
            "    print('[Close] skipped - no open session')",
        ]


class WorkflowCompiler:
    def __init__(self, graph: NodeGraph, logger: Callable[[str], None], sleep_scale: float = 1.0):
        self.graph = graph
        self.logger = logger
        self.sleep_scale = sleep_scale

    def _flow_nodes(self) -> list[InstrumentFlowNode]:
        return sorted(
            [node for node in self.graph.all_nodes() if isinstance(node, InstrumentFlowNode)],
            key=node_sort_key,
        )

    def ordered_nodes(self) -> tuple[list[InstrumentFlowNode], list[InstrumentFlowNode]]:
        nodes = self._flow_nodes()
        starts = [node for node in nodes if isinstance(node, StartNode)]
        if not starts:
            raise WorkflowError("No Start node found. Add a Start node before running the workflow.")

        node_map = {node.id: node for node in nodes}
        reachable_ids: set[str] = set()
        stack = [node.id for node in reversed(starts)]
        while stack:
            node_id = stack.pop()
            if node_id in reachable_ids:
                continue
            reachable_ids.add(node_id)
            node = node_map[node_id]
            targets = sorted(node.flow_targets(), key=node_sort_key, reverse=True)
            for target in targets:
                if target.id in node_map:
                    stack.append(target.id)

        if not reachable_ids:
            raise WorkflowError("No executable nodes were found from Start.")

        edges = {node_id: [] for node_id in reachable_ids}
        indegree = {node_id: 0 for node_id in reachable_ids}
        for node_id in reachable_ids:
            node = node_map[node_id]
            for target in node.flow_targets():
                if target.id not in reachable_ids:
                    continue
                edges[node_id].append(target.id)
                indegree[target.id] += 1

        ready = sorted(
            [node_map[node_id] for node_id, degree in indegree.items() if degree == 0],
            key=node_sort_key,
        )
        ordered: list[InstrumentFlowNode] = []
        while ready:
            node = ready.pop(0)
            ordered.append(node)
            for target_id in sorted(edges[node.id], key=lambda item: node_sort_key(node_map[item])):
                indegree[target_id] -= 1
                if indegree[target_id] == 0:
                    ready.append(node_map[target_id])
                    ready.sort(key=node_sort_key)

        if len(ordered) != len(reachable_ids):
            raise WorkflowError(
                "The reachable graph contains a cycle or ambiguous dependencies. "
                "Keep the workflow acyclic."
            )

        skipped = sorted(
            [node for node in nodes if node.id not in reachable_ids],
            key=node_sort_key,
        )
        return ordered, skipped

    def execute(self) -> RuntimeState:
        ordered_nodes, skipped_nodes = self.ordered_nodes()
        state = RuntimeState(logger=self.logger, sleep_scale=self.sleep_scale)

        self.logger("[Compiler] execution order:")
        for node in ordered_nodes:
            self.logger(f"  - {node.name()} ({node.__class__.__name__})")
        for node in skipped_nodes:
            self.logger(f"[Compiler] skipped unreachable node: {node.name()}")

        current_node: InstrumentFlowNode | None = None
        try:
            for current_node in ordered_nodes:
                current_node.execute(state)
        except Exception as exc:
            node_name = current_node.name() if current_node else "<unknown>"
            raise WorkflowError(f'Execution failed at "{node_name}": {exc}') from exc
        finally:
            if state.api and state.api.is_open:
                self.logger("[Compiler] auto-close open session")
                state.api.close()

        self.logger("[Compiler] workflow completed")
        return state

    def export_python(self, output_path: Path) -> Path:
        ordered_nodes, skipped_nodes = self.ordered_nodes()
        output_path = ensure_parent_dir(output_path)

        lines = [
            "from __future__ import annotations",
            "",
            "import time",
            "",
            EXPORTED_API_SOURCE,
            "",
            "",
            "def main():",
            "    context = {}",
            "    api = None",
            "    print('[Exported Workflow] start')",
            "",
        ]

        if skipped_nodes:
            lines.append(f"    print({('[Compiler] skipped unreachable nodes: ' + ', '.join(node.name() for node in skipped_nodes))!r})")
            lines.append("")

        for node in ordered_nodes:
            lines.append(f"    # {node.name()} ({node.__class__.__name__})")
            emitted = node.emit_python()
            for line in emitted:
                lines.append(f"    {line}" if line else "")
            lines.append("")

        lines.extend(
            [
                "    if api is not None and api.is_open:",
                "        api.close()",
                "    print('[Exported Workflow] done')",
                "",
                "",
                "if __name__ == '__main__':",
                "    main()",
                "",
            ]
        )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        self.logger(f"[Export] wrote python workflow -> {output_path}")
        return output_path


class InstrumentWorkflowWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeGraphQt Instrument Workflow Demo")
        self.resize(1600, 960)

        self.graph = NodeGraph()
        self.graph.set_layout_direction(LayoutDirectionEnum.HORIZONTAL.value)
        self.graph.set_pipe_collision(True)
        self.graph.set_pipe_slicing(True)
        self.graph.set_acyclic(True)

        self._register_nodes()
        self._build_widgets()
        self._build_ui()
        self._wire_signals()
        self._configure_context_menu()

        self.statusBar().showMessage("Ready")

    def _register_nodes(self) -> None:
        self.graph.register_nodes(
            [
                StartNode,
                OpenInstrumentNode,
                SetOutputNode,
                SetVoltageNode,
                DelayNode,
                MeasureVoltageNode,
                PrintContextNode,
                CloseInstrumentNode,
            ]
        )

    def _build_widgets(self) -> None:
        self.palette = NodesPaletteWidget(node_graph=self.graph)
        self.tree = NodesTreeWidget(node_graph=self.graph)
        self.properties_bin = PropertiesBinWidget(node_graph=self.graph)
        self.properties_bin.set_limit(1)
        self.log_output = QtWidgets.QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(180)

        self.btn_sample = QtWidgets.QPushButton("Load Sample")
        self.btn_auto_layout = QtWidgets.QPushButton("Auto Layout")
        self.btn_save_graph = QtWidgets.QPushButton("Save Graph")
        self.btn_load_graph = QtWidgets.QPushButton("Load Graph")
        self.btn_export_python = QtWidgets.QPushButton("Export Python")
        self.btn_run = QtWidgets.QPushButton("Run Workflow")
        self.btn_clear_log = QtWidgets.QPushButton("Clear Log")

        for widget in (self.palette, self.tree):
            widget.set_category_label("demo.instrument", "Instrument Demo")

        self.palette.set_category_label("nodeGraphQt.nodes", "Builtin Nodes")
        self.tree.set_category_label("nodeGraphQt.nodes", "Builtin Nodes")

    def _build_ui(self) -> None:
        instructions = QtWidgets.QLabel(
            "1. Drag nodes from Palette or Tree.\n"
            "2. Connect flow_out -> flow_in.\n"
            "3. Edit node parameters on the node or in the Properties pane.\n"
            "4. Save graph JSON, export Python, or run the workflow."
        )
        instructions.setWordWrap(True)

        left_tabs = QtWidgets.QTabWidget()
        left_tabs.addTab(self.palette, "Palette")
        left_tabs.addTab(self.tree, "Tree")

        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.addWidget(instructions)
        left_layout.addWidget(left_tabs, 1)

        button_bar = QtWidgets.QHBoxLayout()
        button_bar.addWidget(self.btn_sample)
        button_bar.addWidget(self.btn_auto_layout)
        button_bar.addWidget(self.btn_save_graph)
        button_bar.addWidget(self.btn_load_graph)
        button_bar.addWidget(self.btn_export_python)
        button_bar.addWidget(self.btn_run)
        button_bar.addWidget(self.btn_clear_log)
        button_bar.addStretch(1)

        horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        horizontal_splitter.addWidget(left_panel)
        horizontal_splitter.addWidget(self.graph.widget)
        horizontal_splitter.addWidget(self.properties_bin)
        horizontal_splitter.setSizes([280, 980, 360])

        vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vertical_splitter.addWidget(horizontal_splitter)
        vertical_splitter.addWidget(self.log_output)
        vertical_splitter.setSizes([760, 200])

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(button_bar)
        layout.addWidget(vertical_splitter, 1)
        self.setCentralWidget(central)

    def _wire_signals(self) -> None:
        self.btn_sample.clicked.connect(self.build_sample_flow)
        self.btn_auto_layout.clicked.connect(self.auto_layout)
        self.btn_save_graph.clicked.connect(self.save_graph)
        self.btn_load_graph.clicked.connect(self.load_graph)
        self.btn_export_python.clicked.connect(self.export_python_code)
        self.btn_run.clicked.connect(self.run_workflow)
        self.btn_clear_log.clicked.connect(self.log_output.clear)

        self.graph.node_selected.connect(self.properties_bin.add_node)
        self.graph.node_double_clicked.connect(self.properties_bin.add_node)

    def _configure_context_menu(self) -> None:
        demo_menu = self.graph.context_menu().add_menu("Demo")
        demo_menu.add_command("Run Workflow", self._menu_run_workflow, "Ctrl+R")
        demo_menu.add_command("Export Python", self._menu_export_python, "Ctrl+E")
        demo_menu.add_command("Load Sample", self._menu_load_sample, "Ctrl+Shift+R")

    def _menu_run_workflow(self, graph: NodeGraph) -> None:
        del graph
        self.run_workflow()

    def _menu_export_python(self, graph: NodeGraph) -> None:
        del graph
        self.export_python_code()

    def _menu_load_sample(self, graph: NodeGraph) -> None:
        del graph
        self.build_sample_flow()

    def log(self, message: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} | {message}"
        self.log_output.appendPlainText(line)
        print(line)
        self.statusBar().showMessage(message, 5000)

    def compiler(self, sleep_scale: float = 1.0) -> WorkflowCompiler:
        return WorkflowCompiler(self.graph, logger=self.log, sleep_scale=sleep_scale)

    def auto_layout(self) -> None:
        self.graph.auto_layout_nodes()
        self.graph.fit_to_selection()
        self.log("[UI] auto layout complete")

    def _pick_save_path(self, title: str, default_path: Path, file_filter: str) -> Path | None:
        default_path = ensure_parent_dir(default_path)
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            title,
            str(default_path),
            file_filter,
        )
        return Path(file_path) if file_path else None

    def _pick_open_path(self, title: str, default_path: Path, file_filter: str) -> Path | None:
        default_path = ensure_parent_dir(default_path)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            title,
            str(default_path),
            file_filter,
        )
        return Path(file_path) if file_path else None

    def save_graph(self, path: Path | None = None) -> Path | None:
        try:
            target = path or self._pick_save_path(
                "Save Node Graph",
                DEFAULT_GRAPH_PATH,
                "JSON Files (*.json)",
            )
            if not target:
                return None
            target = ensure_parent_dir(target)
            self.graph.save_session(str(target))
            self.log(f"[Save] graph json -> {target}")
            return target
        except Exception as exc:
            self.log(f"[Save] failed: {exc}")
            traceback.print_exc()
            return None

    def load_graph(self, path: Path | None = None) -> Path | None:
        try:
            target = path or self._pick_open_path(
                "Load Node Graph",
                DEFAULT_GRAPH_PATH,
                "JSON Files (*.json)",
            )
            if not target:
                return None
            self.graph.load_session(str(target))
            self.graph.fit_to_selection()
            self.log(f"[Load] graph json -> {target}")
            return target
        except Exception as exc:
            self.log(f"[Load] failed: {exc}")
            traceback.print_exc()
            return None

    def export_python_code(self, path: Path | None = None) -> Path | None:
        try:
            target = path or self._pick_save_path(
                "Export Python Workflow",
                DEFAULT_EXPORT_PATH,
                "Python Files (*.py)",
            )
            if not target:
                return None
            return self.compiler().export_python(target)
        except Exception as exc:
            self.log(f"[Export] failed: {exc}")
            traceback.print_exc()
            return None

    def run_workflow(self, *, raise_on_error: bool = False, sleep_scale: float = 1.0) -> RuntimeState | None:
        try:
            state = self.compiler(sleep_scale=sleep_scale).execute()
            self.log(f"[Run] context values -> {state.values}")
            return state
        except Exception as exc:
            self.log(f"[Run] failed: {exc}")
            traceback.print_exc()
            if raise_on_error:
                raise
            return None

    def build_sample_flow(self) -> None:
        self.graph.clear_session()
        self.log_output.clear()

        start = self.graph.create_node(StartNode.type_, name="Start", pos=(-700, 0))
        open_node = self.graph.create_node(OpenInstrumentNode.type_, name="Open PSU", pos=(-480, 0))
        output_node = self.graph.create_node(SetOutputNode.type_, name="Enable CH1", pos=(-240, 0))
        set_voltage = self.graph.create_node(SetVoltageNode.type_, name="Set CH1 Voltage", pos=(20, 0))
        delay = self.graph.create_node(DelayNode.type_, name="Settle", pos=(260, 0))
        measure = self.graph.create_node(MeasureVoltageNode.type_, name="Measure CH1", pos=(500, 0))
        printer = self.graph.create_node(PrintContextNode.type_, name="Print Result", pos=(760, 0))
        close_node = self.graph.create_node(CloseInstrumentNode.type_, name="Close PSU", pos=(1040, 0))

        start.set_property("plan_name", "Instrument power-up demo")
        open_node.set_property("resource_name", "TCPIP0::192.168.0.8::INSTR")
        output_node.set_property("channel", "CH1")
        output_node.set_property("enabled", True)
        set_voltage.set_property("channel", "CH1")
        set_voltage.set_property("voltage", "5.0")
        delay.set_property("seconds", "0.1")
        measure.set_property("channel", "CH1")
        measure.set_property("save_as", "measured_voltage")
        printer.set_property("message", "Measured voltage")
        printer.set_property("context_key", "measured_voltage")

        start.set_output(0, open_node.input(0))
        open_node.set_output(0, output_node.input(0))
        output_node.set_output(0, set_voltage.input(0))
        set_voltage.set_output(0, delay.input(0))
        delay.set_output(0, measure.input(0))
        measure.set_output(0, printer.input(0))
        printer.set_output(0, close_node.input(0))

        backdrop = self.graph.create_node("Backdrop", name="Instrument Flow")
        if isinstance(backdrop, BackdropNode):
            backdrop.set_text("Visual programming demo: edit nodes, save JSON, export Python, run workflow.")
            backdrop.wrap_nodes([start, open_node, output_node, set_voltage, delay, measure, printer, close_node])

        self.auto_layout()
        self.log("[Sample] demo workflow ready")


def create_qapplication() -> QtWidgets.QApplication:
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    return app


def run_qt_app(app: QtWidgets.QApplication) -> int:
    if hasattr(app, "exec"):
        return app.exec()
    return app.exec_()


def run_headless_smoke_test() -> int:
    app = create_qapplication()
    window = InstrumentWorkflowWindow()
    window.show()
    app.processEvents()

    window.build_sample_flow()
    app.processEvents()

    graph_path = window.save_graph(DEFAULT_GRAPH_PATH)
    if not graph_path:
        raise WorkflowError("Failed to save graph during smoke test.")

    export_path = window.export_python_code(DEFAULT_EXPORT_PATH)
    if not export_path:
        raise WorkflowError("Failed to export python during smoke test.")

    window.run_workflow(raise_on_error=True, sleep_scale=0.0)

    loaded = window.load_graph(graph_path)
    if not loaded:
        raise WorkflowError("Failed to reload graph during smoke test.")

    window.run_workflow(raise_on_error=True, sleep_scale=0.0)

    result = subprocess.run(
        [sys.executable, str(export_path)],
        cwd=str(export_path.parent),
        capture_output=True,
        text=True,
        check=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    window.log(f"[SmokeTest] exported python executed -> {export_path}")
    window.close()
    app.processEvents()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="NodeGraphQt instrument workflow demo")
    parser.add_argument(
        HEADLESS_SMOKE_FLAG,
        action="store_true",
        help="Run save/load/export/execute validation without keeping the UI open.",
    )
    args = parser.parse_args()

    if args.headless_smoke_test:
        return run_headless_smoke_test()

    app = create_qapplication()
    window = InstrumentWorkflowWindow()
    window.build_sample_flow()
    window.show()
    return run_qt_app(app)


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .common import ensure_parent_directory, sanitize_identifier
from .nodes import WorkflowNode
from .workflow_runtime import analyze_flow_graph

# Markers for tooling / smoke tests to extract suggested imports (lines are valid Python after stripping leading "# ").
_EXPORT_IMPORTS_BEGIN = "# __DEMO02_EXPORT_IMPORTS__"
_EXPORT_IMPORTS_END = "# __DEMO02_EXPORT_IMPORTS_END__"

DEFAULT_FLOW_BODY_NAME = "instrument_flow_body"


@dataclass
class ExportContext:
    api_imports: dict[str, set[str]] = field(default_factory=dict)
    general_helper_required: bool = False
    _session_vars: dict[str, str] = field(default_factory=dict)
    _used_names: set[str] = field(default_factory=set)
    _node_functions: dict[str, str] = field(default_factory=dict)

    def require_api_import(self, module_name: str | None, class_name: str | None) -> None:
        if not module_name or not class_name:
            return
        self.api_imports.setdefault(module_name, set()).add(class_name)

    def require_general_helper(self) -> None:
        self.general_helper_required = True

    def session_var(self, session_name: str) -> str:
        if session_name in self._session_vars:
            return self._session_vars[session_name]
        base = sanitize_identifier(f"session_{session_name}", "session_var")
        candidate = base
        suffix = 2
        while candidate in self._used_names:
            candidate = f"{base}_{suffix}"
            suffix += 1
        self._used_names.add(candidate)
        self._session_vars[session_name] = candidate
        return candidate

    def node_function_name(self, node: WorkflowNode) -> str:
        if node.id in self._node_functions:
            return self._node_functions[node.id]
        base = sanitize_identifier(f"node_{node.id}", "node_func")
        candidate = base
        suffix = 2
        while candidate in self._used_names:
            candidate = f"{base}_{suffix}"
            suffix += 1
        self._used_names.add(candidate)
        self._node_functions[node.id] = candidate
        return candidate


def _suggested_import_lines(export_context: ExportContext) -> list[str]:
    """Comment lines (with # prefix) listing suggested top-level imports for the host module."""
    lines = [_EXPORT_IMPORTS_BEGIN]
    lines.append("# from demo_02.common import as_bool, as_float, as_int, as_text")
    if export_context.general_helper_required:
        lines.append("# from demo_02.Instruments_pythonic import general as general_helpers")
    for module_name in sorted(export_context.api_imports):
        class_names = ", ".join(sorted(export_context.api_imports[module_name]))
        if module_name.startswith("demo_02."):
            mod = module_name
        else:
            mod = f"demo_02.{module_name}"
        lines.append(f"# from {mod} import {class_names}")
    lines.append(_EXPORT_IMPORTS_END)
    return lines


class WorkflowExporter:
    """Exports NODE FLOW as a single function body (embeddable in test cases / apps)."""

    def __init__(self, graph: Any, *, flow_body_name: str = DEFAULT_FLOW_BODY_NAME) -> None:
        self.graph = graph
        self._flow_body_name = flow_body_name

    def render_code(self) -> str:
        analysis = analyze_flow_graph(self.graph)
        export_context = ExportContext()
        flow_links: dict[str, dict[str, str]] = {}

        node_blocks: list[tuple[str, str, str, list[str]]] = []
        for node in analysis.reachable_nodes:
            function_name = export_context.node_function_name(node)
            flow_links[node.id] = {}
            for spec in node.flow_output_specs():
                target = node.next_flow_node(spec.key)
                if target is not None:
                    flow_links[node.id][spec.key] = target.id
            emitted_lines = node.emit_python(export_context) or ["return None"]
            node_blocks.append(
                (function_name, node.name(), node.__class__.__name__, list(emitted_lines)),
            )

        header = [
            "# Demo 02 — NODE FLOW 导出（仅函数体）",
            "#",
            "# 本文件只包含「仪器 API 调用与控制流调度」对应的 Python 函数体，便于您：",
            "#   - 粘贴到测试用例中并自行命名外层函数 / 类方法；",
            "#   - 在外层补充夹具、断言、报告等应用逻辑。",
            "#",
            "# 默认入口：单函数 "
            + self._flow_body_name
            + "(context)（实际定义在文件下方；本行注释勿含可被误匹配的 def 片段）。",
            "# context：由宿主传入的可变 dict；本函数会 setdefault sessions / port_values / variables 等键。",
            "#",
            "# 请将「建议 import」复制到您的模块顶部（路径以工程 PYTHONPATH 为准）：",
        ]
        header.extend(_suggested_import_lines(export_context))

        body_lines: list[str] = [
            "",
            f"def {self._flow_body_name}(context):",
            '    """Execute the node-graph flow (instrument API call sequence + branching). Mutates `context`."""',
            "    def _read_input_value(context, source, fallback=None):",
            "        if source is None:",
            "            return fallback",
            "        source_key = tuple(source)",
            "        if source_key not in context['port_values']:",
            "            raise RuntimeError(f'Upstream data not ready: {source_key[0]}:{source_key[1]}')",
            "        return context['port_values'][source_key]",
            "",
            "    def _set_output_value(context, node_id, key, value):",
            "        context['port_values'][(node_id, key)] = value",
            "        return value",
            "",
        ]

        for function_name, node_name, class_name, emitted_lines in node_blocks:
            body_lines.append(f"    def {function_name}(context):")
            body_lines.append(f"        # {node_name} ({class_name})")
            for line in emitted_lines:
                body_lines.append(f"        {line}")
            body_lines.append("")

        unreachable_names = [node.name() for node in analysis.unreachable_nodes]
        body_lines.extend(
            [
                f"    _FLOW_LINKS = {flow_links!r}",
                f"    _UNREACHABLE_NODE_NAMES = {unreachable_names!r}",
                "    _NODE_NAMES = {",
            ]
        )
        for node in analysis.reachable_nodes:
            body_lines.append(f"        {node.id!r}: {node.name()!r},")
        body_lines.extend(
            [
                "    }",
                "    _NODE_DISPATCH = {",
            ]
        )
        for node in analysis.reachable_nodes:
            fn = export_context.node_function_name(node)
            body_lines.append(f"        {node.id!r}: {fn},")
        body_lines.extend(
            [
                "    }",
                f"    _START_NODE_ID = {analysis.start_nodes[0].id!r}",
                "",
                "    context.setdefault('sessions', {})",
                "    context.setdefault('api_instances', {})",
                "    context.setdefault('variables', {})",
                "    context.setdefault('logs', [])",
                "    context.setdefault('last_result', None)",
                "    context.setdefault('return_value', None)",
                "    context.setdefault('port_values', {})",
                "    context.setdefault('loop_states', {})",
                "    context.setdefault('terminated', False)",
                "",
                "    current_node_id = _START_NODE_ID",
                "    step_count = 0",
                "    try:",
                "        while current_node_id:",
                "            step_count += 1",
                "            if step_count > 10000:",
                "                raise RuntimeError('Flow exceeded 10000 execution steps.')",
                "            next_flow_key = _NODE_DISPATCH[current_node_id](context)",
                "            if context.get('terminated'):",
                "                break",
                "            current_node_id = _FLOW_LINKS.get(current_node_id, {}).get(next_flow_key)",
            ]
        )
        body_lines.extend(
            [
                "    finally:",
                "        for session_name, session in list(context['sessions'].items()):",
                "            if getattr(session, 'initialized', False):",
                "                session.close()",
                "",
                "    return context.get('return_value', context.get('last_result'))",
                "",
            ]
        )

        sections = header + [""] + body_lines
        return "\n".join(sections)

    def export_to_file(self, file_path: Path) -> Path:
        file_path = ensure_parent_directory(file_path)
        file_path.write_text(self.render_code() + "\n", encoding="utf-8")
        return file_path

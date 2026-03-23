from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .common import BASE_DIR as DEMO_BASE_DIR, ensure_parent_directory, sanitize_identifier
from .nodes import WorkflowNode
from .workflow_runtime import analyze_flow_graph


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


class WorkflowExporter:
    def __init__(self, graph: Any) -> None:
        self.graph = graph

    def render_code(self) -> str:
        analysis = analyze_flow_graph(self.graph)
        export_context = ExportContext()
        function_sections: list[str] = []
        flow_links: dict[str, dict[str, str]] = {}

        for node in analysis.reachable_nodes:
            function_name = export_context.node_function_name(node)
            flow_links[node.id] = {}
            for spec in node.flow_output_specs():
                target = node.next_flow_node(spec.key)
                if target is not None:
                    flow_links[node.id][spec.key] = target.id

            function_sections.append(f"def {function_name}(context):")
            function_sections.append(f"    # {node.name()} ({node.__class__.__name__})")
            emitted_lines = node.emit_python(export_context) or ["return None"]
            for line in emitted_lines:
                function_sections.append(f"    {line}")
            function_sections.append("")

        import_lines = [
            "from __future__ import annotations",
            "",
            "import sys",
            "from pathlib import Path",
            "",
            f"BASE_DIR = Path(r'{DEMO_BASE_DIR}')",
            "if str(BASE_DIR) not in sys.path:",
            "    sys.path.insert(0, str(BASE_DIR))",
            "",
            "from common import as_bool, as_float, as_int, as_text",
            "",
        ]

        if export_context.general_helper_required:
            import_lines.append("from Instruments_pythonic import general as general_helpers")

        for module_name in sorted(export_context.api_imports):
            class_names = ", ".join(sorted(export_context.api_imports[module_name]))
            import_lines.append(f"from {module_name} import {class_names}")

        helper_lines = [
            "",
            "",
            f"START_NODE_ID = {analysis.start_nodes[0].id!r}",
            f"FLOW_LINKS = {flow_links!r}",
            f"UNREACHABLE_NODES = {[node.name() for node in analysis.unreachable_nodes]!r}",
            "NODE_NAMES = {",
        ]
        for node in analysis.reachable_nodes:
            helper_lines.append(f"    {node.id!r}: {node.name()!r},")
        helper_lines.extend(
            [
                "}",
                "",
                "def _read_input_value(context, source, fallback=None):",
                "    if source is None:",
                "        return fallback",
                "    source_key = tuple(source)",
                "    if source_key not in context['port_values']:",
                "        raise RuntimeError(f'Upstream data not ready: {source_key[0]}:{source_key[1]}')",
                "    return context['port_values'][source_key]",
                "",
                "def _set_output_value(context, node_id, key, value):",
                "    context['port_values'][(node_id, key)] = value",
                "    return value",
                "",
                "NODE_DISPATCH = {",
            ]
        )
        for node in analysis.reachable_nodes:
            helper_lines.append(f"    {node.id!r}: {export_context.node_function_name(node)},")
        helper_lines.extend(
            [
                "}",
                "",
                "",
                "def run_flow(context=None):",
                "    if context is None:",
                "        context = {}",
                "    context.setdefault('sessions', {})",
                "    context.setdefault('api_instances', {})",
                "    context.setdefault('variables', {})",
                "    context.setdefault('logs', [])",
                "    context.setdefault('last_result', None)",
                "    context.setdefault('return_value', None)",
                "    context.setdefault('port_values', {})",
                "    context.setdefault('loop_states', {})",
                "    context.setdefault('terminated', False)",
                "    print('[Exported Flow] start')",
                "    if UNREACHABLE_NODES:",
                "        print('[Warning] unreachable nodes:', ', '.join(UNREACHABLE_NODES))",
                "    current_node_id = START_NODE_ID",
                "    step_count = 0",
                "    try:",
                "        while current_node_id:",
                "            step_count += 1",
                "            if step_count > 10000:",
                "                raise RuntimeError('Flow exceeded 10000 execution steps.')",
                "            print(f\"[Exported Flow] node -> {NODE_NAMES.get(current_node_id, current_node_id)}\")",
                "            next_flow_key = NODE_DISPATCH[current_node_id](context)",
                "            if context.get('terminated'):",
                "                break",
                "            current_node_id = FLOW_LINKS.get(current_node_id, {}).get(next_flow_key)",
                "        print('[Exported Flow] done')",
                "        return context.get('return_value', context.get('last_result'))",
                "    finally:",
            ]
        )

        footer = [
            "        for session_name, session in list(context['sessions'].items()):",
            "            if getattr(session, 'initialized', False):",
            "                session.close()",
            "                print(f'[Exported Flow] auto close session: {session_name}')",
            "",
            "",
            "def main():",
            "    result = run_flow()",
            "    print('[Exported Flow] return ->', result)",
            "",
            "",
            "if __name__ == '__main__':",
            "    main()",
            "",
        ]

        sections = import_lines + function_sections + helper_lines + footer
        return "\n".join(line for line in sections if line != "")

    def export_to_file(self, file_path: Path) -> Path:
        file_path = ensure_parent_directory(file_path)
        file_path.write_text(self.render_code() + "\n", encoding="utf-8")
        return file_path

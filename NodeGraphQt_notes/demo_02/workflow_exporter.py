"""
Export NODE FLOW as a short linear Python script: one statement per node in graph visit order.

Uses ``demo_02.Instruments_pythonic.general`` helpers (``delay``, ``comment``, …) and a single
``run_flow()`` wrapper so ``return`` is valid. Rename ``run_flow`` when embedding in tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .api_dynamic_nodes import DynamicApiMethodNode
from .common import as_bool, as_float, as_int, as_text, ensure_parent_directory, sanitize_identifier
from .nodes import (
    BooleanConstantNode,
    BooleanLogicNode,
    BooleanNotNode,
    CloseSessionNode,
    CommentNode,
    CompareNumberNode,
    CompareTextNode,
    DelayNode,
    FloatConstantNode,
    IntegerConstantNode,
    MathBinaryNode,
    OpenInstrumentSessionNode,
    PythonSnippetNode,
    RaiseErrorNode,
    ReadBoolVariableNode,
    ReadIntVariableNode,
    ReadTextVariableNode,
    ReturnNode,
    SessionMethodNode,
    SetVariableNode,
    StartNode,
    TextConstantNode,
    WorkflowNode,
)
from .workflow_runtime import analyze_flow_graph


@dataclass
class ExportContext:
    """Used by execute_debug / emit_python on nodes (unchanged API)."""

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


class _ScriptContext:
    """Tracks imports, session names, and API instance vars for linear script."""

    def __init__(self) -> None:
        self.api_imports: dict[str, set[str]] = {}
        self.session_vars: dict[str, str] = {}
        self.api_instance_vars: dict[str, str] = {}
        self.general_names: set[str] = set()

    def need_general(self, *names: str) -> None:
        self.general_names.update(names)

    def require_api(self, module: str | None, class_name: str | None) -> None:
        if not module or not class_name:
            return
        self.api_imports.setdefault(module, set()).add(class_name)

    def session_py_var(self, session_name: str) -> str:
        if session_name in self.session_vars:
            return self.session_vars[session_name]
        base = "".join(c if c.isalnum() else "_" for c in session_name) or "session"
        if base[0].isdigit():
            base = "s_" + base
        v = base
        n = 2
        all_names = set(self.session_vars.values())
        while v in all_names:
            v = f"{base}_{n}"
            n += 1
        self.session_vars[session_name] = v
        return v

    def api_instance_var(self, instance_key: str, class_name: str) -> tuple[str, bool]:
        if instance_key in self.api_instance_vars:
            return self.api_instance_vars[instance_key], False
        base = "".join(c if c.isalnum() else "_" for c in class_name) or "api"
        v = f"_api_{base}"
        used = set(self.api_instance_vars.values()) | set(self.session_vars.values())
        n = 2
        while v in used:
            v = f"_api_{base}_{n}"
            n += 1
        self.api_instance_vars[instance_key] = v
        return v, True


def _module_import_path(relative: str) -> str:
    if relative.startswith("demo_02."):
        return relative
    return f"demo_02.{relative}"


def _linear_lines_for_node(node: WorkflowNode, sctx: _ScriptContext) -> list[str]:
    """Emit 0+ lines (no indent) for one node; empty => skip."""

    if isinstance(node, StartNode):
        return []  # user-visible script stays minimal; title is not a runtime call

    if isinstance(node, CommentNode):
        sctx.need_general("comment")
        msg = as_text(node.field_value("message"))
        return [f"comment({msg!r})", f"_last = {msg!r}"]

    if isinstance(node, DelayNode):
        sctx.need_general("delay")
        sec = as_float(node.field_value("seconds"))
        return [f"delay({sec!r})", f"_last = {sec!r}"]

    if isinstance(node, SetVariableNode):
        sctx.need_general("set_variable")
        name = as_text(node.field_value("variable_name"))
        kind = as_text(node.field_value("value_type"))
        raw = node.get_property("value")
        if kind == "int":
            val = as_int(raw)
        elif kind == "float":
            val = as_float(raw)
        elif kind == "bool":
            val = as_bool(raw)
        else:
            val = as_text(raw)
        return [f"set_variable(variables, {name!r}, {val!r})", f"_last = variables[{name!r}]"]

    if isinstance(node, ReturnNode):
        sctx.need_general("return_value")
        st = as_text(node.field_value("source_type"))
        if st == "constant":
            return [f"return return_value({node.field_value('value')!r})"]
        if st == "variable":
            vn = as_text(node.field_value("variable_name"))
            return [f"return return_value(variables.get({vn!r}))"]
        return ["return return_value(_last)"]

    if isinstance(node, RaiseErrorNode):
        sctx.need_general("raise_error")
        return [f"raise_error({as_text(node.field_value('message'))!r})"]

    if isinstance(node, BooleanConstantNode):
        v = as_bool(node.get_property("value"))
        return [f"_last = {v!r}"]

    if isinstance(node, IntegerConstantNode):
        v = as_int(node.get_property("value"))
        return [f"_last = {v!r}"]

    if isinstance(node, FloatConstantNode):
        v = as_float(node.get_property("value"))
        return [f"_last = {v!r}"]

    if isinstance(node, TextConstantNode):
        v = as_text(node.get_property("value"))
        return [f"_last = {v!r}"]

    if isinstance(node, ReadTextVariableNode):
        vn = as_text(node.field_value("variable_name"))
        dv = as_text(node.field_value("default_value"))
        return [f"_last = variables.get({vn!r}, {dv!r})"]

    if isinstance(node, ReadBoolVariableNode):
        vn = as_text(node.field_value("variable_name"))
        dv = as_bool(node.get_property("default_value"))
        return [f"_last = variables.get({vn!r}, {dv!r})"]

    if isinstance(node, ReadIntVariableNode):
        vn = as_text(node.field_value("variable_name"))
        dv = as_int(node.get_property("default_value"))
        return [f"_last = variables.get({vn!r}, {dv!r})"]

    if isinstance(node, MathBinaryNode):
        op = as_text(node.field_value("operator"))
        fl = as_float(node.get_property("left"))
        fr = as_float(node.get_property("right"))
        expr = {"add": f"{fl!r} + {fr!r}", "sub": f"{fl!r} - {fr!r}", "mul": f"{fl!r} * {fr!r}", "div": f"({fl!r} / {fr!r}) if {fr!r} != 0 else 0.0"}[
            op
        ]
        return [f"_last = {expr}"]

    if isinstance(node, CompareNumberNode):
        op = as_text(node.field_value("operator"))
        fl = as_float(node.get_property("left"))
        fr = as_float(node.get_property("right"))
        expr = {
            "eq": f"{fl!r} == {fr!r}",
            "ne": f"{fl!r} != {fr!r}",
            "gt": f"{fl!r} > {fr!r}",
            "ge": f"{fl!r} >= {fr!r}",
            "lt": f"{fl!r} < {fr!r}",
            "le": f"{fl!r} <= {fr!r}",
        }[op]
        return [f"_last = {expr}"]

    if isinstance(node, CompareTextNode):
        op = as_text(node.field_value("operator"))
        tl = as_text(node.get_property("left"))
        tr = as_text(node.get_property("right"))
        expr = {
            "eq": f"{tl!r} == {tr!r}",
            "ne": f"{tl!r} != {tr!r}",
            "contains": f"{tr!r} in {tl!r}",
            "starts_with": f"{tl!r}.startswith({tr!r})",
            "ends_with": f"{tl!r}.endswith({tr!r})",
        }[op]
        return [f"_last = {expr}"]

    if isinstance(node, BooleanLogicNode):
        op = as_text(node.field_value("operator"))
        fl = as_bool(node.get_property("left"))
        fr = as_bool(node.get_property("right"))
        expr = {"and": f"{fl!r} and {fr!r}", "or": f"{fl!r} or {fr!r}", "xor": f"bool({fl!r}) ^ bool({fr!r})"}[op]
        return [f"_last = {expr}"]

    if isinstance(node, BooleanNotNode):
        fv = as_bool(node.get_property("value"))
        return [f"_last = (not {fv!r})"]

    if isinstance(node, OpenInstrumentSessionNode):
        mod = node.API_MODULE
        cls = node.API_CLASS_NAME
        sctx.require_api(mod, cls)
        var = sctx.session_py_var(node.session_name_value())
        sn = node.session_name_value()
        return [
            f"{var} = {cls}()",
            (
                f"{var}.initialize(resource_name={as_text(node.field_value('resource_name'))!r}, "
                f"id_query={as_bool(node.field_value('id_query'))!r}, "
                f"reset={as_bool(node.field_value('reset'))!r})"
            ),
            f"sessions[{sn!r}] = {var}",
            f"_last = {var}",
        ]

    if isinstance(node, CloseSessionNode):
        var = sctx.session_py_var(node.session_name_value())
        return [f"{var}.close()", "_last = None"]

    if isinstance(node, SessionMethodNode) and not isinstance(node, CloseSessionNode):
        mod = node.API_MODULE
        cls = node.API_CLASS_NAME
        if mod and cls:
            sctx.require_api(mod, cls)
        var = sctx.session_py_var(node.session_name_value())
        args = ", ".join(f"{f}={node.field_value(f)!r}" for f in node.METHOD_ARG_FIELDS)
        call = f"{var}.{node.METHOD_NAME}({args})"
        if node.RESULT_TO_VARIABLE:
            save = as_text(node.field_value("save_as"))
            return [f"variables[{save!r}] = {call}", f"_last = variables[{save!r}]"]
        return [f"_last = {call}"]

    if isinstance(node, DynamicApiMethodNode):
        meta = node._api_meta()  # noqa: SLF001
        if meta.is_control_node:
            return [f"# TODO: control node {meta.method_name} — flatten if/while/for manually"]
        sctx.require_api(meta.export_module_name, meta.class_name)
        var, need_new = sctx.api_instance_var(meta.instance_key, meta.class_name)
        kwargs = ", ".join(f"{p.name}={node.get_property(p.name)!r}" for p in meta.params)
        call = f"{var}.{meta.method_name}({kwargs})"
        if need_new:
            return [f"{var} = {meta.class_name}()", f"_last = {call}"]
        return [f"_last = {call}"]

    if isinstance(node, PythonSnippetNode):
        return [f"# TODO: Python 代码块节点 {node.name()} — 请手写或改用通用节点"]

    return [f"# TODO: {node.name()} ({node.__class__.__name__}) — linear export not mapped"]


DEFAULT_RUN_FLOW_NAME = "run_flow"


class WorkflowExporter:
    def __init__(self, graph: Any, *, run_flow_name: str = DEFAULT_RUN_FLOW_NAME) -> None:
        self.graph = graph
        self._run_flow_name = run_flow_name

    def render_code(self) -> str:
        analysis = analyze_flow_graph(self.graph)
        sctx = _ScriptContext()

        body_lines: list[str] = []
        for node in analysis.ordered_nodes:
            for line in _linear_lines_for_node(node, sctx):
                body_lines.append("    " + line)

        import_lines: list[str] = [
            '"""NODE FLOW → linear Python (visit order). Rename run_flow() in your tests."""',
            "from __future__ import annotations",
            "",
            "from typing import Any",
            "",
        ]
        if sctx.general_names:
            g = ", ".join(sorted(sctx.general_names))
            import_lines.append(f"from demo_02.Instruments_pythonic.general import {g}")
            import_lines.append("")
        for mod in sorted(sctx.api_imports):
            classes = ", ".join(sorted(sctx.api_imports[mod]))
            import_lines.append(f"from {_module_import_path(mod)} import {classes}")
        if sctx.api_imports:
            import_lines.append("")

        func = [
            "",
            f"def {self._run_flow_name}() -> Any:",
            '    """Instrument API call sequence from the graph (minimal linear form)."""',
            "    variables: dict[str, Any] = {}",
            "    sessions: dict[str, Any] = {}",
            "    _last: Any = None",
            "",
        ]
        footer = [
            "",
            "",
            f"# __DEMO02_EXPORT_IMPORTS__",
            f"# (copy imports above into your module if you paste only the function body)",
            f"# __DEMO02_EXPORT_IMPORTS_END__",
            "",
        ]

        return "\n".join(import_lines + func + body_lines + footer)

    def export_to_file(self, file_path: Path) -> Path:
        file_path = ensure_parent_directory(file_path)
        file_path.write_text(self.render_code() + "\n", encoding="utf-8")
        return file_path

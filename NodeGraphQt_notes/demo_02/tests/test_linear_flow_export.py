"""Linear NODE FLOW → Python export: shape checks + exec run_flow()."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

NOTES_DIR = Path(__file__).resolve().parent.parent.parent
if str(NOTES_DIR) not in sys.path:
    sys.path.insert(0, str(NOTES_DIR))

NODEGRAPH_ROOT = NOTES_DIR.parent / "NodeGraphQt"
if str(NODEGRAPH_ROOT) not in sys.path:
    sys.path.insert(0, str(NODEGRAPH_ROOT))

from Qt import QtWidgets  # noqa: E402
from NodeGraphQt import NodeGraph  # noqa: E402

from demo_02.node_registry import ensure_instrument_api_registered, register_all_nodes  # noqa: E402
from demo_02.nodes import CommentNode, DelayNode, ReturnNode, StartNode  # noqa: E402
from demo_02.workflow_exporter import DEFAULT_RUN_FLOW_NAME, WorkflowExporter  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _qt_app() -> QtWidgets.QApplication:
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


def _make_graph() -> NodeGraph:
    g = NodeGraph()
    register_all_nodes(g)
    ensure_instrument_api_registered(g)
    return g


def test_export_contains_delay_and_comment_literals() -> None:
    g = _make_graph()
    start = g.create_node(StartNode.type_, name="开始")
    comment = g.create_node(CommentNode.type_, name="注释")
    delay = g.create_node(DelayNode.type_, name="延时")
    ret = g.create_node(ReturnNode.type_, name="返回")
    comment.set_property("message", "My comment")
    delay.set_property("seconds", 1.0)
    ret.set_property("source_type", "last_result")
    start.set_output(0, comment.input(0))
    comment.set_output(0, delay.input(0))
    delay.set_output(0, ret.input(0))

    code = WorkflowExporter(g).render_code()
    assert "delay(1.0)" in code
    assert 'comment("My comment")' in code or "comment('My comment')" in code
    assert "def run_flow()" in code
    assert "return return_value(_last)" in code
    assert "NODE_DISPATCH" not in code
    assert "instrument_flow_body" not in code


def test_exec_run_flow_smoke() -> None:
    g = _make_graph()
    start = g.create_node(StartNode.type_, name="开始")
    comment = g.create_node(CommentNode.type_, name="注释")
    delay = g.create_node(DelayNode.type_, name="延时")
    ret = g.create_node(ReturnNode.type_, name="返回")
    comment.set_property("message", "ok")
    delay.set_property("seconds", 0.0)
    ret.set_property("source_type", "last_result")
    start.set_output(0, comment.input(0))
    comment.set_output(0, delay.input(0))
    delay.set_output(0, ret.input(0))

    code = WorkflowExporter(g).render_code()
    ns: dict = {"__builtins__": __builtins__}
    exec(compile(code, "<export>", "exec"), ns, ns)
    fn = ns[DEFAULT_RUN_FLOW_NAME]
    out = fn()
    assert out == 0.0  # delay sets _last to seconds


@pytest.mark.parametrize(
    "source_type,prop_key,prop_val,expect",
    [
        ("constant", "value", "done", "done"),
        ("variable", "variable_name", "x", None),
    ],
)
def test_return_node_export(source_type: str, prop_key: str, prop_val: str, expect: object | None) -> None:
    g = _make_graph()
    s = g.create_node(StartNode.type_, name="s")
    r = g.create_node(ReturnNode.type_, name="r")
    r.set_property("source_type", source_type)
    r.set_property(prop_key, prop_val)
    if source_type == "variable":
        r.set_property("value", "unused")
    s.set_output(0, r.input(0))
    code = WorkflowExporter(g).render_code()
    ns: dict = {"__builtins__": __builtins__}
    exec(compile(code, "<export>", "exec"), ns, ns)
    out = ns[DEFAULT_RUN_FLOW_NAME]()
    assert out == expect

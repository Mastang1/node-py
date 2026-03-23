"""
Composition root for the node graph widget: single place to register nodes and apply
editor-wide policies (acyclicity off, pipe modes, layout direction, connection hooks).
"""
from __future__ import annotations

from typing import Any, Callable

from NodeGraphQt import NodeGraph
from NodeGraphQt.constants import LayoutDirectionEnum

from .node_registry import register_all_nodes

# Callbacks match NodeGraphQt viewer hooks (return types vary by binding).
ConnectionValidator = Callable[..., Any]
ConnectionFeedback = Callable[..., Any] | None


def build_configured_node_graph(
    connection_validator: ConnectionValidator,
    connection_feedback_callback: ConnectionFeedback = None,
) -> NodeGraph:
    """
    Build a NodeGraph ready for Demo 02: all node types registered, instrument-friendly
    graph policies, and viewer connection validation wired from the UI layer.
    """
    graph = NodeGraph()
    register_all_nodes(graph)
    graph.set_acyclic(False)
    graph.set_pipe_collision(True)
    graph.set_pipe_slicing(True)
    graph.set_layout_direction(LayoutDirectionEnum.HORIZONTAL.value)
    viewer = graph.viewer()
    viewer.connection_validator = connection_validator
    viewer.connection_feedback_callback = connection_feedback_callback
    return graph

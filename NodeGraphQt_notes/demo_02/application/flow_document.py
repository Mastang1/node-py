"""
Application-layer document handle: file identity on disk + dirty state via undo stack.

Presentation (MainWindow) should treat this as the source of truth for *path* and *is_dirty*,
while the actual graph topology lives on NodeGraphQt.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NodeGraphQt import NodeGraph


class FlowDocument:
    __slots__ = ("_graph", "path")

    def __init__(self, graph: NodeGraph) -> None:
        self._graph = graph
        self.path: Path | None = None

    @property
    def graph(self) -> NodeGraph:
        return self._graph

    def is_dirty(self) -> bool:
        return not self._graph.undo_stack().isClean()

    def mark_clean(self) -> None:
        self._graph.undo_stack().setClean()

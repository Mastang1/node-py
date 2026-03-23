from __future__ import annotations

from typing import Any, Callable

from Qt import QtCore

from .nodes import WorkflowNode
from .workflow_debug import DebugSession, DebugStepInfo
from .workflow_runtime import FlowExecutionResult, WorkflowRuntime


class FlowDebugWorker(QtCore.QThread):
    """Runs WorkflowRuntime.execute_debug in a background thread."""

    paused_at = QtCore.Signal(object)  # DebugStepInfo
    run_finished = QtCore.Signal(object)  # FlowExecutionResult | None
    run_failed = QtCore.Signal(str)
    run_stopped = QtCore.Signal()

    def __init__(
        self,
        graph: Any,
        log_callback: Callable[[str, str], None],
        language: str,
        session: DebugSession,
        node_state_callback: Callable[[WorkflowNode, str, dict[str, Any]], None] | None,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._graph = graph
        self._log_callback = log_callback
        self._language = language
        self.session = session
        self._node_state_callback = node_state_callback

    def run(self) -> None:
        runtime = WorkflowRuntime(
            self._graph,
            self._log_callback,
            language=self._language,
            node_state_callback=self._node_state_callback,
        )
        try:
            result = runtime.execute_debug(self.session, on_paused=self._on_paused)
            self.run_finished.emit(result)
        except Exception as exc:
            self.run_failed.emit(str(exc))

    def _on_paused(self, info: DebugStepInfo) -> None:
        self.paused_at.emit(info)

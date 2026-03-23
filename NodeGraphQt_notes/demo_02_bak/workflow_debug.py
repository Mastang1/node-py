from __future__ import annotations

import threading
from dataclasses import dataclass

from .nodes import WorkflowNode


class DebugStopped(Exception):
    """User stopped debug session before flow finished."""


@dataclass
class DebugStepInfo:
    """Snapshot shown in UI when execution pauses before a node."""

    node: WorkflowNode
    step_index: int
    python_lines: list[str]
    export_function_name: str

    @property
    def snippet_text(self) -> str:
        header = f"# {self.node.name()} ({self.node.__class__.__name__}) -> {self.export_function_name}(context)"
        body = "\n".join(self.python_lines) if self.python_lines else "pass"
        return f"{header}\n{body}"


class DebugSession:
    """
    Thread-safe controller used by WorkflowRuntime.execute_debug.

    Modes:
    - hold: blocked until user chooses Step or Continue.
    - go_one: run exactly one node, then return to hold.
    - go_free: run until a breakpoint or flow end; breakpoints force hold.
    """

    def __init__(self) -> None:
        self._cv = threading.Condition()
        self._stopped = False
        self._mode = "hold"  # hold | go_one | go_free
        self._breakpoints: set[str] = set()

    @property
    def breakpoints(self) -> set[str]:
        return set(self._breakpoints)

    def stop(self) -> None:
        with self._cv:
            self._stopped = True
            self._cv.notify_all()

    def reset_for_new_run(self) -> None:
        with self._cv:
            self._stopped = False
            self._mode = "hold"
            self._cv.notify_all()

    def step_over(self) -> None:
        with self._cv:
            self._mode = "go_one"
            self._cv.notify()

    def continue_run(self) -> None:
        with self._cv:
            self._mode = "go_free"
            self._cv.notify()

    def set_breakpoint(self, node_id: str, enabled: bool) -> None:
        with self._cv:
            if enabled:
                self._breakpoints.add(node_id)
            else:
                self._breakpoints.discard(node_id)

    def toggle_breakpoint(self, node_id: str) -> bool:
        """Returns True if breakpoint is now enabled."""
        with self._cv:
            if node_id in self._breakpoints:
                self._breakpoints.discard(node_id)
                return False
            self._breakpoints.add(node_id)
            return True

    def has_breakpoint(self, node_id: str) -> bool:
        with self._cv:
            return node_id in self._breakpoints

    def clear_breakpoints(self) -> None:
        with self._cv:
            self._breakpoints.clear()
            self._cv.notify_all()

    def wait_before_node(self, node_id: str) -> None:
        with self._cv:
            while True:
                if self._stopped:
                    raise DebugStopped()
                if self._mode == "go_free":
                    if node_id in self._breakpoints:
                        self._mode = "hold"
                        continue
                    return
                if self._mode == "go_one":
                    return
                self._cv.wait()

    def after_node_executed(self) -> None:
        with self._cv:
            if self._mode == "go_one":
                self._mode = "hold"

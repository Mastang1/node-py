from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .Instruments_pythonic import general as general_helpers
from .common import LANG_ZH
from .nodes import StartNode, WorkflowNode
from .workflow_debug import DebugSession, DebugStepInfo, DebugStopped


def node_sort_key(node: WorkflowNode) -> tuple[float, float, str, str]:
    return (round(node.y_pos(), 3), round(node.x_pos(), 3), node.name(), node.id)


class WorkflowAnalysisError(RuntimeError):
    pass


class WorkflowRuntimeError(RuntimeError):
    pass


@dataclass
class FlowAnalysis:
    ordered_nodes: list[WorkflowNode]
    reachable_nodes: list[WorkflowNode]
    unreachable_nodes: list[WorkflowNode]
    start_nodes: list[WorkflowNode]


@dataclass
class FlowContext:
    log_callback: Callable[[str, str], None]
    sessions: dict[str, Any] = field(default_factory=dict)
    api_instances: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    port_values: dict[tuple[str, str], Any] = field(default_factory=dict)
    loop_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    last_result: Any = None
    return_value: Any = None
    logs: list[dict[str, str]] = field(default_factory=list)
    terminated: bool = False
    node_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    language: str = LANG_ZH
    general_helpers: Any = general_helpers

    def log(self, channel: str, message: str) -> None:
        self.logs.append({"channel": channel, "message": message})
        self.log_callback(channel, message)

    def set_port_value(self, node_id: str, key: str, value: Any) -> None:
        self.port_values[(node_id, key)] = value

    def get_port_value(self, node_id: str, key: str) -> Any:
        port_key = (node_id, key)
        if port_key not in self.port_values:
            raise RuntimeError(f"上游数据端口尚未产生值: {node_id}:{key}")
        return self.port_values[port_key]


@dataclass
class FlowExecutionResult:
    analysis: FlowAnalysis
    context: FlowContext


def analyze_flow_graph(graph: Any) -> FlowAnalysis:
    nodes = sorted(
        [node for node in graph.all_nodes() if isinstance(node, WorkflowNode)],
        key=node_sort_key,
    )
    if not nodes:
        raise WorkflowAnalysisError("当前流程中没有可执行节点。")

    start_nodes = [node for node in nodes if isinstance(node, StartNode)]
    if not start_nodes:
        raise WorkflowAnalysisError("当前流程缺少 Start 节点。")
    if len(start_nodes) > 1:
        raise WorkflowAnalysisError("当前流程只允许存在一个 Start 节点。")

    reachable_ids: set[str] = set()
    stack = [start_nodes[0]]
    node_map = {node.id: node for node in nodes}
    while stack:
        current = stack.pop()
        if current.id in reachable_ids:
            continue
        reachable_ids.add(current.id)
        for spec in reversed(current.flow_output_specs()):
            for target in reversed(sorted(current.flow_targets(spec.key), key=node_sort_key)):
                if target.id in node_map:
                    stack.append(target)

    reachable_nodes = [node for node in nodes if node.id in reachable_ids]
    unreachable_nodes = [node for node in nodes if node.id not in reachable_ids]

    return FlowAnalysis(
        ordered_nodes=reachable_nodes,
        reachable_nodes=sorted(reachable_nodes, key=node_sort_key),
        unreachable_nodes=sorted(unreachable_nodes, key=node_sort_key),
        start_nodes=start_nodes,
    )


class WorkflowRuntime:
    def __init__(
        self,
        graph: Any,
        log_callback: Callable[[str, str], None],
        *,
        language: str = LANG_ZH,
        node_state_callback: Callable[[WorkflowNode, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.graph = graph
        self.log_callback = log_callback
        self.language = language
        self.node_state_callback = node_state_callback

    def _emit_node_state(self, node: WorkflowNode, status: str, payload: dict[str, Any]) -> None:
        if self.node_state_callback:
            self.node_state_callback(node, status, payload)

    def _next_flow_node(self, node: WorkflowNode, next_flow_key: str | None) -> WorkflowNode | None:
        if next_flow_key:
            return node.next_flow_node(next_flow_key)
        return node.next_flow_node()

    def execute(self) -> FlowExecutionResult:
        analysis = analyze_flow_graph(self.graph)
        context = FlowContext(log_callback=self.log_callback, language=self.language)

        for node in analysis.unreachable_nodes:
            context.log("validate", f"未执行不可达节点: {node.name()}")

        context.log("run", "流程可达节点如下:")
        for node in analysis.reachable_nodes:
            context.log("run", f" - {node.name()} ({node.__class__.__name__})")

        current_node: WorkflowNode | None = None
        current_node = analysis.start_nodes[0]
        step_count = 0
        try:
            while current_node is not None:
                step_count += 1
                if step_count > 10_000:
                    raise WorkflowRuntimeError("流程执行步数超过 10000，疑似存在未收敛循环。")
                self._emit_node_state(current_node, "running", {"message": "running"})
                context.log("run", f"执行节点: {current_node.name()}")
                event = current_node.execute(context)
                for key, value in event.output_values.items():
                    context.set_port_value(current_node.id, key, value)
                payload = {
                    "summary": event.summary,
                    "payload": event.payload,
                    "next_flow_key": event.next_flow_key,
                }
                context.node_states[current_node.id] = {
                    "status": "success",
                    **payload,
                }
                self._emit_node_state(current_node, "success", payload)
                context.log("run", f"完成节点: {current_node.name()} -> {event.summary}")
                if context.terminated:
                    context.log("run", f"流程已在节点 {current_node.name()} 处终止。")
                    break
                next_node = self._next_flow_node(current_node, event.next_flow_key)
                if next_node is None:
                    context.log("run", f"节点 {current_node.name()} 没有后续控制流，流程结束。")
                current_node = next_node
        except Exception as exc:
            if current_node:
                payload = {"message": str(exc)}
                context.node_states[current_node.id] = {
                    "status": "error",
                    "summary": str(exc),
                    "payload": payload,
                }
                self._emit_node_state(current_node, "error", payload)
                raise WorkflowRuntimeError(f'节点 "{current_node.name()}" 执行失败: {exc}') from exc
            raise WorkflowRuntimeError(str(exc)) from exc
        finally:
            for session_name, session in list(context.sessions.items()):
                if getattr(session, "initialized", False):
                    try:
                        session.close()
                        context.log("run", f"自动关闭会话: {session_name}")
                    except Exception as exc:  # pragma: no cover - best effort cleanup
                        context.log("run", f"自动关闭会话失败 {session_name}: {exc}")

        return FlowExecutionResult(analysis=analysis, context=context)

    def execute_debug(
        self,
        session: DebugSession,
        *,
        on_paused: Callable[[DebugStepInfo], None] | None = None,
    ) -> FlowExecutionResult | None:
        """
        Same as execute(), but pauses before each node according to DebugSession.
        Emits DebugStepInfo via on_paused (called from worker thread) before blocking wait.
        Returns None if user stopped early (DebugStopped).
        """
        from .workflow_exporter import ExportContext

        export_ctx = ExportContext()
        analysis = analyze_flow_graph(self.graph)
        context = FlowContext(log_callback=self.log_callback, language=self.language)

        for node in analysis.unreachable_nodes:
            context.log("validate", f"未执行不可达节点: {node.name()}")

        context.log("run", "[调试] 流程可达节点如下:")
        for node in analysis.reachable_nodes:
            context.log("run", f" - {node.name()} ({node.__class__.__name__})")

        current_node: WorkflowNode | None = analysis.start_nodes[0]
        step_count = 0
        step_index = 0
        try:
            while current_node is not None:
                step_count += 1
                if step_count > 10_000:
                    raise WorkflowRuntimeError("流程执行步数超过 10000，疑似存在未收敛循环。")

                step_index += 1
                fn_name = export_ctx.node_function_name(current_node)
                py_lines = current_node.emit_python(export_ctx) or ["return None"]
                info = DebugStepInfo(
                    node=current_node,
                    step_index=step_index,
                    python_lines=list(py_lines),
                    export_function_name=fn_name,
                )
                if on_paused:
                    on_paused(info)
                session.wait_before_node(current_node.id)

                self._emit_node_state(current_node, "running", {"message": "debug"})
                context.log("run", f"[调试] 执行节点: {current_node.name()}")
                event = current_node.execute(context)
                for key, value in event.output_values.items():
                    context.set_port_value(current_node.id, key, value)
                payload = {
                    "summary": event.summary,
                    "payload": event.payload,
                    "next_flow_key": event.next_flow_key,
                }
                context.node_states[current_node.id] = {
                    "status": "success",
                    **payload,
                }
                self._emit_node_state(current_node, "success", payload)
                context.log("run", f"[调试] 完成节点: {current_node.name()} -> {event.summary}")
                session.after_node_executed()

                if context.terminated:
                    context.log("run", f"流程已在节点 {current_node.name()} 处终止。")
                    break
                next_node = self._next_flow_node(current_node, event.next_flow_key)
                if next_node is None:
                    context.log("run", f"节点 {current_node.name()} 没有后续控制流，流程结束。")
                current_node = next_node
        except DebugStopped:
            context.log("run", "[调试] 用户已停止调试。")
            return None
        except Exception as exc:
            if current_node:
                payload = {"message": str(exc)}
                context.node_states[current_node.id] = {
                    "status": "error",
                    "summary": str(exc),
                    "payload": payload,
                }
                self._emit_node_state(current_node, "error", payload)
                raise WorkflowRuntimeError(f'节点 "{current_node.name()}" 执行失败: {exc}') from exc
            raise WorkflowRuntimeError(str(exc)) from exc
        finally:
            for session_name, sess in list(context.sessions.items()):
                if getattr(sess, "initialized", False):
                    try:
                        sess.close()
                        context.log("run", f"自动关闭会话: {session_name}")
                    except Exception as exc:  # pragma: no cover - best effort cleanup
                        context.log("run", f"自动关闭会话失败 {session_name}: {exc}")

        return FlowExecutionResult(analysis=analysis, context=context)

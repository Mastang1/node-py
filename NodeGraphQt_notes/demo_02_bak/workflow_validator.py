from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import as_text, data_type_compatible
from .nodes import RaiseErrorNode, ReturnNode, WorkflowNode
from .workflow_runtime import FlowAnalysis, WorkflowAnalysisError, analyze_flow_graph


@dataclass
class ValidationMessage:
    level: str
    message: str


class WorkflowValidator:
    def __init__(self, graph: Any) -> None:
        self.graph = graph

    @staticmethod
    def has_errors(messages: list[ValidationMessage]) -> bool:
        return any(message.level == "error" for message in messages)

    def validate(self) -> tuple[list[ValidationMessage], FlowAnalysis | None]:
        messages: list[ValidationMessage] = []
        try:
            analysis = analyze_flow_graph(self.graph)
        except WorkflowAnalysisError as exc:
            return [ValidationMessage("error", str(exc))], None

        for node in analysis.unreachable_nodes:
            messages.append(ValidationMessage("warning", f"存在不可达节点: {node.name()}"))

        opened_sessions: dict[str, str] = {}
        for index, node in enumerate(analysis.ordered_nodes):
            self._validate_required_fields(node, messages)
            self._validate_required_data_inputs(node, messages)
            self._validate_connected_data_types(node, messages)
            self._validate_session_binding(node, opened_sessions, messages)
            self._validate_flow_outputs(node, messages)

            if isinstance(node, ReturnNode) and any(node.flow_targets(spec.key) for spec in node.flow_output_specs()):
                messages.append(ValidationMessage("warning", f"Return 节点仍连接了后续控制流: {node.name()}"))
            if isinstance(node, RaiseErrorNode) and any(node.flow_targets(spec.key) for spec in node.flow_output_specs()):
                messages.append(ValidationMessage("warning", f"Raise Error 节点仍连接了后续控制流: {node.name()}"))

        if not self.has_errors(messages):
            try:
                from .workflow_exporter import WorkflowExporter

                WorkflowExporter(self.graph).render_code()
            except Exception as exc:
                messages.append(ValidationMessage("error", f"导出代码预检查失败: {exc}"))

        if not messages:
            messages.append(ValidationMessage("info", "流程校验通过。"))
        elif not self.has_errors(messages):
            messages.append(ValidationMessage("info", "流程校验通过，但包含警告。"))

        return messages, analysis

    def _validate_required_fields(self, node: WorkflowNode, messages: list[ValidationMessage]) -> None:
        for field in node.field_specs():
            if not field.required:
                continue
            value = node.get_property(field.name)
            if field.kind == "bool":
                continue
            if field.kind in {"int", "float"}:
                if value in (None, ""):
                    messages.append(ValidationMessage("error", f"节点 {node.name()} 缺少必填参数 {field.name}"))
                continue
            if not as_text(value):
                messages.append(ValidationMessage("error", f"节点 {node.name()} 缺少必填参数 {field.name}"))

    def _validate_session_binding(
        self,
        node: WorkflowNode,
        opened_sessions: dict[str, str],
        messages: list[ValidationMessage],
    ) -> None:
        binding = getattr(node, "SESSION_BINDING", "none")
        session_kind = getattr(node, "SESSION_KIND", None)
        session_name = as_text(node.get_property("session_name")) if "session_name" in node.field_map() else ""

        if binding == "open":
            if not session_name:
                messages.append(ValidationMessage("error", f"节点 {node.name()} 缺少 session_name"))
                return
            if session_name in opened_sessions:
                messages.append(ValidationMessage("error", f"会话名重复定义: {session_name}"))
                return
            opened_sessions[session_name] = session_kind or ""
            return

        if binding in {"use", "close"}:
            if not session_name:
                messages.append(ValidationMessage("error", f"节点 {node.name()} 缺少 session_name"))
                return
            if session_name not in opened_sessions:
                messages.append(ValidationMessage("error", f"节点 {node.name()} 引用了未打开的会话 {session_name}"))
                return
            opened_kind = opened_sessions[session_name]
            if session_kind and opened_kind and session_kind != opened_kind:
                messages.append(
                    ValidationMessage(
                        "error",
                        f"节点 {node.name()} 会话类型不匹配: 需要 {session_kind}，实际为 {opened_kind}",
                    )
                )

    def _validate_required_data_inputs(self, node: WorkflowNode, messages: list[ValidationMessage]) -> None:
        for spec in node.data_input_specs():
            if not spec.required:
                continue
            if node.connected_data_source(spec.key) is not None:
                continue
            if spec.key in node.field_map():
                value = node.get_property(spec.key)
                if spec.data_type == "bool":
                    continue
                if spec.data_type in {"int", "float"} and value not in (None, ""):
                    continue
                if as_text(value):
                    continue
            messages.append(ValidationMessage("error", f"节点 {node.name()} 缺少数据输入 {spec.label}"))

    def _validate_connected_data_types(self, node: WorkflowNode, messages: list[ValidationMessage]) -> None:
        for spec in node.data_input_specs():
            source = node.connected_data_source(spec.key)
            if source is None:
                continue
            source_node, source_key = source
            source_spec = source_node.data_output_spec(source_key)
            if not data_type_compatible(source_spec.data_type, spec.data_type):
                messages.append(
                    ValidationMessage(
                        "error",
                        f"节点 {node.name()} 的输入 {spec.label} 类型为 {spec.data_type}，"
                        f"但上游 {source_node.name()} 输出的是 {source_spec.data_type}",
                    )
                )

    def _validate_flow_outputs(self, node: WorkflowNode, messages: list[ValidationMessage]) -> None:
        if len(node.flow_output_specs()) <= 1:
            return
        for spec in node.flow_output_specs():
            if node.flow_targets(spec.key):
                continue
            messages.append(ValidationMessage("warning", f"节点 {node.name()} 的控制出口 {spec.label} 尚未连接"))

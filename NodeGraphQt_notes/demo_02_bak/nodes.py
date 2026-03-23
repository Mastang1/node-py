from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from NodeGraphQt import BaseNode

from .common import (
    FLOW_IN,
    FLOW_OUT,
    LANG_EN,
    LANG_ZH,
    FieldSpec,
    as_bool,
    as_float,
    as_int,
    as_text,
    normalize_data_type,
    resolve_node_icon_path,
)
from .Instruments_pythonic.digital_pattern_generator import SimDigitalPatternGeneratorIvi
from .Instruments_pythonic.multi_serial_card import SimMultiSerialCardIvi
from .Instruments_pythonic.signal_generator import SimSignalGeneratorIvi


def session_name_field(default: str) -> FieldSpec:
    return FieldSpec(
        name="session_name",
        kind="str",
        default=default,
        label_zh="会话名",
        label_en="Session Name",
        tooltip_zh="用于绑定仪器会话的唯一名称。",
        tooltip_en="Unique name used to bind the instrument session.",
        required=True,
        placeholder_zh="例如 sg_main",
        placeholder_en="For example sg_main",
    )


def resource_name_field(default: str) -> FieldSpec:
    return FieldSpec(
        name="resource_name",
        kind="str",
        default=default,
        label_zh="资源名",
        label_en="Resource Name",
        tooltip_zh="模拟 IVI/VISA 资源名。",
        tooltip_en="Simulated IVI/VISA resource name.",
        required=True,
    )


def save_as_field(default: str) -> FieldSpec:
    return FieldSpec(
        name="save_as",
        kind="str",
        default=default,
        label_zh="保存变量名",
        label_en="Save As",
        tooltip_zh="把返回值保存到 context['variables'] 中的变量名。",
        tooltip_en="Variable name stored in context['variables'].",
        required=True,
    )


def channel_field(default: str = "CH1") -> FieldSpec:
    return FieldSpec(
        name="channel",
        kind="enum",
        default=default,
        label_zh="通道",
        label_en="Channel",
        tooltip_zh="仪器通道名。",
        tooltip_en="Instrument channel name.",
        options=("CH1", "CH2", "CH3", "CH4"),
        required=True,
    )


def bool_field(name: str, default: bool, zh: str, en: str, tooltip_zh: str, tooltip_en: str) -> FieldSpec:
    return FieldSpec(
        name=name,
        kind="bool",
        default=default,
        label_zh=zh,
        label_en=en,
        tooltip_zh=tooltip_zh,
        tooltip_en=tooltip_en,
    )


def float_field(
    name: str,
    default: float,
    zh: str,
    en: str,
    tooltip_zh: str,
    tooltip_en: str,
    *,
    required: bool = True,
) -> FieldSpec:
    return FieldSpec(
        name=name,
        kind="float",
        default=default,
        label_zh=zh,
        label_en=en,
        tooltip_zh=tooltip_zh,
        tooltip_en=tooltip_en,
        required=required,
    )


def int_field(
    name: str,
    default: int,
    zh: str,
    en: str,
    tooltip_zh: str,
    tooltip_en: str,
    *,
    required: bool = True,
) -> FieldSpec:
    return FieldSpec(
        name=name,
        kind="int",
        default=default,
        label_zh=zh,
        label_en=en,
        tooltip_zh=tooltip_zh,
        tooltip_en=tooltip_en,
        required=required,
    )


def text_field(
    name: str,
    default: str,
    zh: str,
    en: str,
    tooltip_zh: str,
    tooltip_en: str,
    *,
    required: bool = False,
    multiline: bool = False,
) -> FieldSpec:
    return FieldSpec(
        name=name,
        kind="multiline" if multiline else "str",
        default=default,
        label_zh=zh,
        label_en=en,
        tooltip_zh=tooltip_zh,
        tooltip_en=tooltip_en,
        required=required,
        multiline=multiline,
    )


def enum_field(
    name: str,
    default: str,
    zh: str,
    en: str,
    tooltip_zh: str,
    tooltip_en: str,
    options: tuple[str, ...],
    *,
    required: bool = True,
) -> FieldSpec:
    return FieldSpec(
        name=name,
        kind="enum",
        default=default,
        label_zh=zh,
        label_en=en,
        tooltip_zh=tooltip_zh,
        tooltip_en=tooltip_en,
        options=options,
        required=required,
    )


@dataclass
class RuntimeEvent:
    summary: str
    payload: Any = None
    next_flow_key: str | None = None
    output_values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DataPortSpec:
    key: str
    label: str
    data_type: str = "str"
    tooltip: str = ""
    required: bool = False
    multi_connection: bool = False


@dataclass(frozen=True)
class FlowPortSpec:
    key: str
    label: str
    display_name: bool = False
    multi_connection: bool = False


_DATA_PORT_COLORS: dict[str, tuple[int, int, int]] = {
    "any": (148, 163, 184),
    "handle": (167, 85, 247),
    "bool": (34, 197, 94),
    "int": (59, 130, 246),
    "float": (14, 165, 233),
    "enum": (245, 158, 11),
    "str": (99, 102, 241),
    "var_ref": (236, 72, 153),
}


def data_port_color(data_type: str) -> tuple[int, int, int]:
    return _DATA_PORT_COLORS.get(str(data_type).strip().lower(), (99, 102, 241))


class WorkflowNode(BaseNode):
    __identifier__ = "demo02.nodes"

    NODE_NAME = "节点"
    DISPLAY_NAME_ZH: ClassVar[str] = "节点"
    DISPLAY_NAME_EN: ClassVar[str] = "Node"
    CATEGORY_ZH: ClassVar[str] = "通用"
    CATEGORY_EN: ClassVar[str] = "General"
    DESCRIPTION_ZH: ClassVar[str] = "工作流节点"
    DESCRIPTION_EN: ClassVar[str] = "Workflow node"
    COLOR: ClassVar[tuple[int, int, int]] = (62, 88, 120)
    ICON_NAME: ClassVar[str] = ""
    FLOW_INPUT_ENABLED: ClassVar[bool] = True
    FLOW_OUTPUT_ENABLED: ClassVar[bool] = True
    FLOW_INPUT_SPECS: ClassVar[tuple[FlowPortSpec, ...]] = (FlowPortSpec(FLOW_IN, FLOW_IN, False, False),)
    FLOW_OUTPUT_SPECS: ClassVar[tuple[FlowPortSpec, ...]] = (FlowPortSpec(FLOW_OUT, FLOW_OUT, False, False),)
    DATA_INPUT_SPECS: ClassVar[tuple[DataPortSpec, ...]] = ()
    DATA_OUTPUT_SPECS: ClassVar[tuple[DataPortSpec, ...]] = ()
    FIELD_SPECS: ClassVar[tuple[FieldSpec, ...]] = ()
    SESSION_BINDING: ClassVar[str] = "none"
    SESSION_KIND: ClassVar[str | None] = None
    API_MODULE: ClassVar[str | None] = None
    API_CLASS_NAME: ClassVar[str | None] = None

    def __init__(self) -> None:
        super().__init__()
        self.set_color(*self.COLOR)
        border_color = tuple(min(255, channel + 48) for channel in self.COLOR) + (255,)
        self.model.border_color = border_color
        self.view.border_color = border_color
        self.model.text_color = (247, 250, 255, 235)
        self.view.text_color = self.model.text_color
        self.set_icon(self.icon_path())
        for spec in self.flow_input_specs():
            self.add_input(
                spec.label,
                multi_input=spec.multi_connection,
                display_name=spec.display_name,
                color=(214, 168, 92),
            )
        for spec in self.data_input_specs():
            self.add_input(
                spec.label,
                multi_input=spec.multi_connection,
                display_name=True,
                color=data_port_color(spec.data_type),
            )
        for spec in self.flow_output_specs():
            self.add_output(
                spec.label,
                multi_output=spec.multi_connection,
                display_name=spec.display_name,
                color=(72, 176, 152),
            )
        for spec in self.data_output_specs():
            self.add_output(
                spec.label,
                multi_output=spec.multi_connection,
                display_name=True,
                color=data_port_color(spec.data_type),
            )
        for field in self.field_specs():
            self.create_property(field.name, field.default)
        if hasattr(self.view, "setToolTip"):
            self.view.setToolTip(self.description(LANG_ZH))

    @classmethod
    def field_specs(cls) -> tuple[FieldSpec, ...]:
        return cls.FIELD_SPECS

    @classmethod
    def field_map(cls) -> dict[str, FieldSpec]:
        return {field.name: field for field in cls.field_specs()}

    @classmethod
    def field_spec(cls, name: str) -> FieldSpec:
        return cls.field_map()[name]

    @classmethod
    def flow_input_specs(cls) -> tuple[FlowPortSpec, ...]:
        if not cls.FLOW_INPUT_ENABLED:
            return ()
        return cls.FLOW_INPUT_SPECS

    @classmethod
    def flow_output_specs(cls) -> tuple[FlowPortSpec, ...]:
        if not cls.FLOW_OUTPUT_ENABLED:
            return ()
        return cls.FLOW_OUTPUT_SPECS

    @classmethod
    def data_input_specs(cls) -> tuple[DataPortSpec, ...]:
        return cls.DATA_INPUT_SPECS

    @classmethod
    def data_output_specs(cls) -> tuple[DataPortSpec, ...]:
        return cls.DATA_OUTPUT_SPECS

    @classmethod
    def flow_input_spec(cls, key: str) -> FlowPortSpec:
        for spec in cls.flow_input_specs():
            if spec.key == key:
                return spec
        raise KeyError(key)

    @classmethod
    def flow_output_spec(cls, key: str) -> FlowPortSpec:
        for spec in cls.flow_output_specs():
            if spec.key == key:
                return spec
        raise KeyError(key)

    @classmethod
    def data_input_spec(cls, key: str) -> DataPortSpec:
        for spec in cls.data_input_specs():
            if spec.key == key:
                return spec
        raise KeyError(key)

    @classmethod
    def data_output_spec(cls, key: str) -> DataPortSpec:
        for spec in cls.data_output_specs():
            if spec.key == key:
                return spec
        raise KeyError(key)

    @classmethod
    def data_output_spec_from_label(cls, label: str) -> DataPortSpec | None:
        for spec in cls.data_output_specs():
            if spec.label == label:
                return spec
        return None

    @classmethod
    def data_input_spec_from_label(cls, label: str) -> DataPortSpec | None:
        for spec in cls.data_input_specs():
            if spec.label == label:
                return spec
        return None

    @classmethod
    def flow_input_spec_from_label(cls, label: str) -> FlowPortSpec | None:
        for spec in cls.flow_input_specs():
            if spec.label == label:
                return spec
        return None

    @classmethod
    def flow_output_spec_from_label(cls, label: str) -> FlowPortSpec | None:
        for spec in cls.flow_output_specs():
            if spec.label == label:
                return spec
        return None

    @classmethod
    def display_name(cls, language: str = LANG_ZH) -> str:
        return cls.DISPLAY_NAME_ZH if language == LANG_ZH else cls.DISPLAY_NAME_EN

    @classmethod
    def category_name(cls, language: str = LANG_ZH) -> str:
        return cls.CATEGORY_ZH if language == LANG_ZH else cls.CATEGORY_EN

    @classmethod
    def description(cls, language: str = LANG_ZH) -> str:
        return cls.DESCRIPTION_ZH if language == LANG_ZH else cls.DESCRIPTION_EN

    @classmethod
    def icon_name(cls) -> str:
        return cls.ICON_NAME

    @classmethod
    def icon_path(cls) -> str:
        return resolve_node_icon_path(cls.icon_name(), cls.category_name(LANG_EN))

    def field_value(self, name: str) -> Any:
        spec = self.field_spec(name)
        raw_value = self.get_property(name)
        if spec.kind == "int":
            return as_int(raw_value, as_int(spec.default))
        if spec.kind == "float":
            return as_float(raw_value, as_float(spec.default))
        if spec.kind == "bool":
            return as_bool(raw_value)
        if spec.kind in {"str", "enum", "multiline"}:
            return as_text(raw_value, as_text(spec.default))
        return raw_value

    def session_name_value(self) -> str:
        return as_text(self.get_property("session_name"))

    def flow_input_port(self, key: str = FLOW_IN) -> Any:
        try:
            spec = self.flow_input_spec(key)
        except KeyError:
            return None
        return self.inputs().get(spec.label)

    def flow_output_port(self, key: str = FLOW_OUT) -> Any:
        try:
            spec = self.flow_output_spec(key)
        except KeyError:
            return None
        return self.outputs().get(spec.label)

    def data_input_port(self, key: str) -> Any:
        try:
            spec = self.data_input_spec(key)
        except KeyError:
            return None
        return self.inputs().get(spec.label)

    def data_output_port(self, key: str) -> Any:
        try:
            spec = self.data_output_spec(key)
        except KeyError:
            return None
        return self.outputs().get(spec.label)

    def flow_targets(self, key: str = FLOW_OUT) -> list["WorkflowNode"]:
        port = self.flow_output_port(key)
        if not port:
            return []
        return [item.node() for item in port.connected_ports() if isinstance(item.node(), WorkflowNode)]

    def flow_sources(self) -> list["WorkflowNode"]:
        sources: list[WorkflowNode] = []
        for spec in self.flow_input_specs():
            port = self.inputs().get(spec.label)
            if not port:
                continue
            for item in port.connected_ports():
                if isinstance(item.node(), WorkflowNode):
                    sources.append(item.node())
        return sources

    def next_flow_node(self, key: str | None = None) -> "WorkflowNode" | None:
        if key:
            targets = self.flow_targets(key)
            return targets[0] if targets else None
        for spec in self.flow_output_specs():
            targets = self.flow_targets(spec.key)
            if targets:
                return targets[0]
        return None

    def connected_data_source(self, key: str) -> tuple["WorkflowNode", str] | None:
        port = self.data_input_port(key)
        if not port:
            return None
        connected = port.connected_ports()
        if not connected:
            return None
        source_port = connected[0]
        source_node = source_port.node()
        if not isinstance(source_node, WorkflowNode):
            return None
        source_spec = source_node.data_output_spec_from_label(source_port.name())
        if source_spec is None:
            return None
        return source_node, source_spec.key

    def coerce_data_value(self, value: Any, data_type: str, default: Any = None) -> Any:
        normalized = normalize_data_type(data_type)
        if normalized == "bool":
            return as_bool(default if value is None else value)
        if normalized == "int":
            return as_int(value, as_int(default) if default is not None else 0)
        if normalized == "float":
            return as_float(value, as_float(default) if default is not None else 0.0)
        if normalized == "any":
            return default if value is None else value
        return as_text(value, as_text(default)) if normalized in {"str", "handle", "var_ref"} else value

    def resolve_data_input_value(self, context: Any, key: str, default: Any = None) -> Any:
        source = self.connected_data_source(key)
        spec = self.data_input_spec(key)
        if source is not None:
            source_node, source_key = source
            return self.coerce_data_value(context.get_port_value(source_node.id, source_key), spec.data_type, default)
        if key in self.field_map():
            return self.coerce_data_value(self.get_property(key), spec.data_type, default)
        return self.coerce_data_value(default, spec.data_type, default)

    def execute(self, context: Any) -> RuntimeEvent:
        raise NotImplementedError

    def emit_python(self, export_context: Any) -> list[str]:
        raise NotImplementedError


class GeneralNode(WorkflowNode):
    CATEGORY_ZH = "通用"
    CATEGORY_EN = "General"
    COLOR = (72, 80, 94)
    ICON_NAME = "logic"


class InstrumentNode(WorkflowNode):
    COLOR = (44, 104, 168)

    def require_session(self, context: Any) -> Any:
        session_name = self.session_name_value()
        if not session_name:
            raise RuntimeError(f"{self.name()} 缺少 session_name。")
        if session_name not in context.sessions:
            raise RuntimeError(f"{self.name()} 找不到会话 {session_name!r}。")
        return context.sessions[session_name]


class OpenInstrumentSessionNode(InstrumentNode):
    SESSION_BINDING = "open"
    API_CLASS: ClassVar[Any] = None

    def execute(self, context: Any) -> RuntimeEvent:
        session_name = self.session_name_value()
        session = self.API_CLASS()
        session.initialize(
            resource_name=self.field_value("resource_name"),
            id_query=self.field_value("id_query"),
            reset=self.field_value("reset"),
        )
        context.sessions[session_name] = session
        context.last_result = session
        return RuntimeEvent(
            summary=f"open session {session_name}",
            payload={"session_name": session_name, "identity": session.get_identity()},
        )

    def emit_python(self, export_context: Any) -> list[str]:
        export_context.require_api_import(self.API_MODULE, self.API_CLASS_NAME)
        session_name = self.session_name_value()
        session_var = export_context.session_var(session_name)
        return [
            f"{session_var} = {self.API_CLASS_NAME}()",
            (
                f"{session_var}.initialize(resource_name={self.field_value('resource_name')!r}, "
                f"id_query={self.field_value('id_query')!r}, reset={self.field_value('reset')!r})"
            ),
            f"context['sessions'][{session_name!r}] = {session_var}",
            f"context['last_result'] = {session_var}",
            f"return {FLOW_OUT!r}",
        ]


class SessionMethodNode(InstrumentNode):
    SESSION_BINDING = "use"
    METHOD_NAME: ClassVar[str] = ""
    METHOD_ARG_FIELDS: ClassVar[tuple[str, ...]] = ()
    RESULT_TO_VARIABLE: ClassVar[bool] = False

    def execute(self, context: Any) -> RuntimeEvent:
        session = self.require_session(context)
        kwargs = {field: self.field_value(field) for field in self.METHOD_ARG_FIELDS}
        result = getattr(session, self.METHOD_NAME)(**kwargs)
        if self.RESULT_TO_VARIABLE:
            save_as = self.field_value("save_as")
            context.variables[save_as] = result
            context.last_result = result
            return RuntimeEvent(
                summary=f"{self.METHOD_NAME} -> {save_as}",
                payload={"save_as": save_as, "value": result},
            )
        context.last_result = result
        return RuntimeEvent(summary=self.METHOD_NAME, payload=result)

    def emit_python(self, export_context: Any) -> list[str]:
        if self.API_MODULE and self.API_CLASS_NAME:
            export_context.require_api_import(self.API_MODULE, self.API_CLASS_NAME)
        session_name = self.session_name_value()
        session_var = export_context.session_var(session_name)
        args_code = ", ".join(
            f"{field}={self.field_value(field)!r}" for field in self.METHOD_ARG_FIELDS
        )
        call_code = f"{session_var}.{self.METHOD_NAME}({args_code})"
        if self.RESULT_TO_VARIABLE:
            save_as = self.field_value("save_as")
            return [
                f"context['variables'][{save_as!r}] = {call_code}",
                f"context['last_result'] = context['variables'][{save_as!r}]",
                f"return {FLOW_OUT!r}",
            ]
        return [
            call_code,
            "context['last_result'] = None",
            f"return {FLOW_OUT!r}",
        ]


class CloseSessionNode(SessionMethodNode):
    SESSION_BINDING = "close"
    METHOD_NAME = "close"
    METHOD_ARG_FIELDS = ()

    def execute(self, context: Any) -> RuntimeEvent:
        session = self.require_session(context)
        session.close()
        context.last_result = None
        return RuntimeEvent(summary=f"close session {self.session_name_value()}")

    def emit_python(self, export_context: Any) -> list[str]:
        session_var = export_context.session_var(self.session_name_value())
        return [
            f"{session_var}.close()",
            "context['last_result'] = None",
            f"return {FLOW_OUT!r}",
        ]


class StartNode(GeneralNode):
    NODE_NAME = "开始"
    DISPLAY_NAME_ZH = "开始"
    DISPLAY_NAME_EN = "Start"
    DESCRIPTION_ZH = "流程起点。"
    DESCRIPTION_EN = "Flow starting point."
    ICON_NAME = "run"
    FLOW_INPUT_ENABLED = False
    COLOR = (36, 118, 94)
    FIELD_SPECS = (
        text_field(
            "title",
            "Demo 02 仪器流程",
            "流程标题",
            "Flow Title",
            "用于说明当前流程的标题。",
            "Title shown in logs and previews.",
            required=True,
        ),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        title = self.field_value("title")
        context.last_result = title
        return RuntimeEvent(summary=f"start {title}", payload=title)

    def emit_python(self, export_context: Any) -> list[str]:
        return [
            f"print({('[Start] ' + self.field_value('title'))!r})",
            f"context['last_result'] = {self.field_value('title')!r}",
            f"return {FLOW_OUT!r}",
        ]


class CommentNode(GeneralNode):
    NODE_NAME = "注释"
    DISPLAY_NAME_ZH = "注释"
    DISPLAY_NAME_EN = "Comment"
    DESCRIPTION_ZH = "仅记录说明文本，不改变流程语义。"
    DESCRIPTION_EN = "Adds documentation text without changing flow semantics."
    ICON_NAME = "preview"
    FIELD_SPECS = (
        text_field(
            "message",
            "这是一个说明节点。",
            "注释内容",
            "Comment",
            "执行时写入日志。",
            "Logged during execution.",
            multiline=True,
        ),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        message = self.field_value("message")
        context.last_result = message
        return RuntimeEvent(summary=f"comment {message}", payload=message)

    def emit_python(self, export_context: Any) -> list[str]:
        export_context.require_general_helper()
        return [
            f"general_helpers.comment({self.field_value('message')!r})",
            f"context['last_result'] = {self.field_value('message')!r}",
            f"return {FLOW_OUT!r}",
        ]


class DelayNode(GeneralNode):
    NODE_NAME = "延时"
    DISPLAY_NAME_ZH = "延时"
    DISPLAY_NAME_EN = "Delay"
    DESCRIPTION_ZH = "阻塞指定秒数。"
    DESCRIPTION_EN = "Blocks for the specified number of seconds."
    COLOR = (142, 108, 58)
    ICON_NAME = "loop"
    FIELD_SPECS = (
        float_field(
            "seconds",
            0.2,
            "延时秒数",
            "Seconds",
            "延时长度，单位秒。",
            "Delay length in seconds.",
        ),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        seconds = self.field_value("seconds")
        context.general_helpers.delay(seconds)
        context.last_result = seconds
        return RuntimeEvent(summary=f"delay {seconds:.3f}s", payload=seconds)

    def emit_python(self, export_context: Any) -> list[str]:
        export_context.require_general_helper()
        return [
            f"general_helpers.delay({self.field_value('seconds')!r})",
            f"context['last_result'] = {self.field_value('seconds')!r}",
            f"return {FLOW_OUT!r}",
        ]


class SetVariableNode(GeneralNode):
    NODE_NAME = "设置变量"
    DISPLAY_NAME_ZH = "设置变量"
    DISPLAY_NAME_EN = "Set Variable"
    DESCRIPTION_ZH = "向 context['variables'] 写入一个变量。"
    DESCRIPTION_EN = "Writes a variable into context['variables']."
    ICON_NAME = "variable"
    FIELD_SPECS = (
        text_field(
            "variable_name",
            "result_value",
            "变量名",
            "Variable Name",
            "要写入的变量名。",
            "Variable name to write.",
            required=True,
        ),
        text_field(
            "value",
            "123",
            "变量值",
            "Value",
            "按变量类型解析的值。",
            "Value parsed according to variable type.",
            required=True,
        ),
        enum_field(
            "value_type",
            "str",
            "变量类型",
            "Value Type",
            "决定 value 的解析方式。",
            "Determines how the value is parsed.",
            ("str", "int", "float", "bool"),
        ),
    )

    def _typed_value(self) -> Any:
        kind = self.field_value("value_type")
        raw_value = self.get_property("value")
        if kind == "int":
            return as_int(raw_value)
        if kind == "float":
            return as_float(raw_value)
        if kind == "bool":
            return as_bool(raw_value)
        return as_text(raw_value)

    def execute(self, context: Any) -> RuntimeEvent:
        name = self.field_value("variable_name")
        value = context.general_helpers.set_variable(context.variables, name, self._typed_value())
        context.last_result = value
        return RuntimeEvent(summary=f"set variable {name}", payload=value)

    def emit_python(self, export_context: Any) -> list[str]:
        export_context.require_general_helper()
        value = self._typed_value()
        name = self.field_value("variable_name")
        return [
            f"general_helpers.set_variable(context['variables'], {name!r}, {value!r})",
            f"context['last_result'] = context['variables'][{name!r}]",
            f"return {FLOW_OUT!r}",
        ]


class ReturnNode(GeneralNode):
    NODE_NAME = "返回"
    DISPLAY_NAME_ZH = "返回"
    DISPLAY_NAME_EN = "Return"
    DESCRIPTION_ZH = "结束流程并返回值。"
    DESCRIPTION_EN = "Terminates the flow and returns a value."
    FLOW_OUTPUT_ENABLED = False
    COLOR = (52, 128, 118)
    ICON_NAME = "export"
    FIELD_SPECS = (
        enum_field(
            "source_type",
            "last_result",
            "返回来源",
            "Return Source",
            "从常量、变量或 last_result 中返回。",
            "Return from constant, variable, or last_result.",
            ("last_result", "constant", "variable"),
        ),
        text_field(
            "value",
            "done",
            "常量值",
            "Constant Value",
            "当 source_type=constant 时使用。",
            "Used when source_type=constant.",
        ),
        text_field(
            "variable_name",
            "result_value",
            "变量名",
            "Variable Name",
            "当 source_type=variable 时使用。",
            "Used when source_type=variable.",
        ),
    )

    def resolve_return_value(self, context: Any) -> Any:
        source_type = self.field_value("source_type")
        if source_type == "constant":
            return self.field_value("value")
        if source_type == "variable":
            return context.variables.get(self.field_value("variable_name"))
        return context.last_result

    def execute(self, context: Any) -> RuntimeEvent:
        value = self.resolve_return_value(context)
        context.return_value = value
        context.last_result = value
        context.terminated = True
        return RuntimeEvent(summary="return", payload=value)

    def emit_python(self, export_context: Any) -> list[str]:
        source_type = self.field_value("source_type")
        if source_type == "constant":
            value_code = repr(self.field_value("value"))
        elif source_type == "variable":
            value_code = f"context['variables'].get({self.field_value('variable_name')!r})"
        else:
            value_code = "context.get('last_result')"
        return [
            f"context['return_value'] = {value_code}",
            "context['last_result'] = context['return_value']",
            "context['terminated'] = True",
            "return None",
        ]


class RaiseErrorNode(GeneralNode):
    NODE_NAME = "抛出错误"
    DISPLAY_NAME_ZH = "抛出错误"
    DISPLAY_NAME_EN = "Raise Error"
    DESCRIPTION_ZH = "抛出异常并终止执行。"
    DESCRIPTION_EN = "Raises an exception and stops execution."
    FLOW_OUTPUT_ENABLED = False
    COLOR = (156, 64, 72)
    ICON_NAME = "stop"
    FIELD_SPECS = (
        text_field(
            "message",
            "示例错误",
            "错误信息",
            "Error Message",
            "抛出的异常信息。",
            "Exception message to raise.",
            required=True,
        ),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        context.general_helpers.raise_error(self.field_value("message"))
        raise AssertionError("unreachable")

    def emit_python(self, export_context: Any) -> list[str]:
        export_context.require_general_helper()
        return [f"general_helpers.raise_error({self.field_value('message')!r})"]


class GeneralValueNode(GeneralNode):
    CATEGORY_ZH = "通用数据"
    CATEGORY_EN = "General Data"
    COLOR = (63, 98, 154)


class GeneralLogicNode(GeneralNode):
    CATEGORY_ZH = "通用逻辑"
    CATEGORY_EN = "General Logic"
    COLOR = (86, 82, 168)
    ICON_NAME = "logic"


class BooleanConstantNode(GeneralValueNode):
    NODE_NAME = "布尔常量"
    DISPLAY_NAME_ZH = "布尔常量"
    DISPLAY_NAME_EN = "Boolean Constant"
    DESCRIPTION_ZH = "输出一个布尔值。"
    DESCRIPTION_EN = "Outputs a boolean value."
    ICON_NAME = "bool"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "布尔值", "bool", "布尔输出值", multi_connection=True),
    )
    FIELD_SPECS = (
        bool_field("value", True, "布尔值", "Value", "常量布尔值。", "Constant boolean value."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_bool(self.get_property("value"))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="bool_constant", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        value = as_bool(self.get_property("value"))
        return [
            f"_set_output_value(context, {self.id!r}, 'value', {value!r})",
            f"context['last_result'] = {value!r}",
            "return 'flow_out'",
        ]


class IntegerConstantNode(GeneralValueNode):
    NODE_NAME = "整数常量"
    DISPLAY_NAME_ZH = "整数常量"
    DISPLAY_NAME_EN = "Integer Constant"
    DESCRIPTION_ZH = "输出一个整数值。"
    DESCRIPTION_EN = "Outputs an integer value."
    ICON_NAME = "number"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "整数值", "int", "整数输出值", multi_connection=True),
    )
    FIELD_SPECS = (
        int_field("value", 0, "整数值", "Value", "常量整数值。", "Constant integer value."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_int(self.get_property("value"))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="int_constant", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        value = as_int(self.get_property("value"))
        return [
            f"_set_output_value(context, {self.id!r}, 'value', {value!r})",
            f"context['last_result'] = {value!r}",
            "return 'flow_out'",
        ]


class FloatConstantNode(GeneralValueNode):
    NODE_NAME = "浮点常量"
    DISPLAY_NAME_ZH = "浮点常量"
    DISPLAY_NAME_EN = "Float Constant"
    DESCRIPTION_ZH = "输出一个浮点值。"
    DESCRIPTION_EN = "Outputs a float value."
    ICON_NAME = "number"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "浮点值", "float", "浮点输出值", multi_connection=True),
    )
    FIELD_SPECS = (
        float_field("value", 0.0, "浮点值", "Value", "常量浮点值。", "Constant float value."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_float(self.get_property("value"))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="float_constant", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        value = as_float(self.get_property("value"))
        return [
            f"_set_output_value(context, {self.id!r}, 'value', {value!r})",
            f"context['last_result'] = {value!r}",
            "return 'flow_out'",
        ]


class TextConstantNode(GeneralValueNode):
    NODE_NAME = "文本常量"
    DISPLAY_NAME_ZH = "文本常量"
    DISPLAY_NAME_EN = "Text Constant"
    DESCRIPTION_ZH = "输出一个文本值。"
    DESCRIPTION_EN = "Outputs a text value."
    ICON_NAME = "text"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "文本值", "str", "文本输出值", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("value", "hello", "文本值", "Value", "常量文本值。", "Constant text value.", required=True),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_text(self.get_property("value"))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="text_constant", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        value = as_text(self.get_property("value"))
        return [
            f"_set_output_value(context, {self.id!r}, 'value', {value!r})",
            f"context['last_result'] = {value!r}",
            "return 'flow_out'",
        ]


class CompareNumberNode(GeneralLogicNode):
    NODE_NAME = "数值比较"
    DISPLAY_NAME_ZH = "数值比较"
    DISPLAY_NAME_EN = "Compare Number"
    DESCRIPTION_ZH = "比较两个数值并输出布尔结果。"
    DESCRIPTION_EN = "Compares two numeric values and outputs a boolean result."
    ICON_NAME = "compare"
    DATA_INPUT_SPECS = (
        DataPortSpec("left", "左值", "float", "左侧数值"),
        DataPortSpec("right", "右值", "float", "右侧数值"),
    )
    DATA_OUTPUT_SPECS = (
        DataPortSpec("result", "比较结果", "bool", "数值比较结果", multi_connection=True),
    )
    FIELD_SPECS = (
        float_field("left", 0.0, "左值", "Left", "未连线时使用的左值。", "Fallback left value."),
        enum_field(
            "operator",
            "eq",
            "比较符",
            "Operator",
            "数值比较运算符。",
            "Numeric comparison operator.",
            ("eq", "ne", "gt", "ge", "lt", "le"),
        ),
        float_field("right", 0.0, "右值", "Right", "未连线时使用的右值。", "Fallback right value."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        left = self.resolve_data_input_value(context, "left", as_float(self.get_property("left")))
        right = self.resolve_data_input_value(context, "right", as_float(self.get_property("right")))
        operator = self.field_value("operator")
        result = {
            "eq": left == right,
            "ne": left != right,
            "gt": left > right,
            "ge": left >= right,
            "lt": left < right,
            "le": left <= right,
        }[operator]
        context.set_port_value(self.id, "result", result)
        context.last_result = result
        return RuntimeEvent(summary="compare_number", payload=result, next_flow_key=FLOW_OUT, output_values={"result": result})

    def emit_python(self, export_context: Any) -> list[str]:
        operator = self.field_value("operator")
        source_left = self.connected_data_source("left")
        source_right = self.connected_data_source("right")
        fallback_left = as_float(self.get_property("left"))
        fallback_right = as_float(self.get_property("right"))
        compare_expr = {
            "eq": "left_value == right_value",
            "ne": "left_value != right_value",
            "gt": "left_value > right_value",
            "ge": "left_value >= right_value",
            "lt": "left_value < right_value",
            "le": "left_value <= right_value",
        }[operator]
        return [
            f"left_value = as_float(_read_input_value(context, {repr((source_left[0].id, source_left[1])) if source_left else 'None'}, {fallback_left!r}))",
            f"right_value = as_float(_read_input_value(context, {repr((source_right[0].id, source_right[1])) if source_right else 'None'}, {fallback_right!r}))",
            f"compare_result = {compare_expr}",
            f"_set_output_value(context, {self.id!r}, 'result', compare_result)",
            "context['last_result'] = compare_result",
            "return 'flow_out'",
        ]


class CompareTextNode(GeneralLogicNode):
    NODE_NAME = "文本比较"
    DISPLAY_NAME_ZH = "文本比较"
    DISPLAY_NAME_EN = "Compare Text"
    DESCRIPTION_ZH = "比较两个文本并输出布尔结果。"
    DESCRIPTION_EN = "Compares two text values and outputs a boolean result."
    ICON_NAME = "compare"
    DATA_INPUT_SPECS = (
        DataPortSpec("left", "左文本", "str", "左侧文本"),
        DataPortSpec("right", "右文本", "str", "右侧文本"),
    )
    DATA_OUTPUT_SPECS = (
        DataPortSpec("result", "比较结果", "bool", "文本比较结果", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("left", "", "左文本", "Left", "未连线时使用的左文本。", "Fallback left text."),
        enum_field(
            "operator",
            "eq",
            "比较符",
            "Operator",
            "文本比较运算符。",
            "Text comparison operator.",
            ("eq", "ne", "contains", "starts_with", "ends_with"),
        ),
        text_field("right", "", "右文本", "Right", "未连线时使用的右文本。", "Fallback right text."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        left = self.resolve_data_input_value(context, "left", self.get_property("left"))
        right = self.resolve_data_input_value(context, "right", self.get_property("right"))
        operator = self.field_value("operator")
        result = {
            "eq": left == right,
            "ne": left != right,
            "contains": right in left,
            "starts_with": left.startswith(right),
            "ends_with": left.endswith(right),
        }[operator]
        context.set_port_value(self.id, "result", result)
        context.last_result = result
        return RuntimeEvent(summary="compare_text", payload=result, next_flow_key=FLOW_OUT, output_values={"result": result})

    def emit_python(self, export_context: Any) -> list[str]:
        operator = self.field_value("operator")
        source_left = self.connected_data_source("left")
        source_right = self.connected_data_source("right")
        fallback_left = as_text(self.get_property("left"))
        fallback_right = as_text(self.get_property("right"))
        compare_expr = {
            "eq": "left_value == right_value",
            "ne": "left_value != right_value",
            "contains": "right_value in left_value",
            "starts_with": "left_value.startswith(right_value)",
            "ends_with": "left_value.endswith(right_value)",
        }[operator]
        return [
            f"left_value = as_text(_read_input_value(context, {repr((source_left[0].id, source_left[1])) if source_left else 'None'}, {fallback_left!r}))",
            f"right_value = as_text(_read_input_value(context, {repr((source_right[0].id, source_right[1])) if source_right else 'None'}, {fallback_right!r}))",
            f"compare_result = {compare_expr}",
            f"_set_output_value(context, {self.id!r}, 'result', compare_result)",
            "context['last_result'] = compare_result",
            "return 'flow_out'",
        ]


class MathBinaryNode(GeneralValueNode):
    NODE_NAME = "数学运算"
    DISPLAY_NAME_ZH = "数学运算"
    DISPLAY_NAME_EN = "Math Binary"
    DESCRIPTION_ZH = "对两个数值执行基础数学运算。"
    DESCRIPTION_EN = "Runs a basic binary math operation on two numeric values."
    ICON_NAME = "number"
    DATA_INPUT_SPECS = (
        DataPortSpec("left", "左值", "float", "左侧数值"),
        DataPortSpec("right", "右值", "float", "右侧数值"),
    )
    DATA_OUTPUT_SPECS = (
        DataPortSpec("result", "运算结果", "float", "数学运算结果", multi_connection=True),
    )
    FIELD_SPECS = (
        float_field("left", 0.0, "左值", "Left", "未连线时使用的左值。", "Fallback left value."),
        enum_field(
            "operator",
            "add",
            "运算符",
            "Operator",
            "数学运算类型。",
            "Math operator.",
            ("add", "sub", "mul", "div"),
        ),
        float_field("right", 0.0, "右值", "Right", "未连线时使用的右值。", "Fallback right value."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        left = self.resolve_data_input_value(context, "left", as_float(self.get_property("left")))
        right = self.resolve_data_input_value(context, "right", as_float(self.get_property("right")))
        operator = self.field_value("operator")
        if operator == "add":
            result = left + right
        elif operator == "sub":
            result = left - right
        elif operator == "mul":
            result = left * right
        else:
            result = left / right if right != 0 else 0.0
        context.set_port_value(self.id, "result", result)
        context.last_result = result
        return RuntimeEvent(summary="math_binary", payload=result, next_flow_key=FLOW_OUT, output_values={"result": result})

    def emit_python(self, export_context: Any) -> list[str]:
        operator = self.field_value("operator")
        source_left = self.connected_data_source("left")
        source_right = self.connected_data_source("right")
        fallback_left = as_float(self.get_property("left"))
        fallback_right = as_float(self.get_property("right"))
        expr = {
            "add": "left_value + right_value",
            "sub": "left_value - right_value",
            "mul": "left_value * right_value",
            "div": "(left_value / right_value) if right_value != 0 else 0.0",
        }[operator]
        return [
            f"left_value = as_float(_read_input_value(context, {repr((source_left[0].id, source_left[1])) if source_left else 'None'}, {fallback_left!r}))",
            f"right_value = as_float(_read_input_value(context, {repr((source_right[0].id, source_right[1])) if source_right else 'None'}, {fallback_right!r}))",
            f"math_result = {expr}",
            f"_set_output_value(context, {self.id!r}, 'result', math_result)",
            "context['last_result'] = math_result",
            "return 'flow_out'",
        ]


class BooleanLogicNode(GeneralLogicNode):
    NODE_NAME = "布尔逻辑"
    DISPLAY_NAME_ZH = "布尔逻辑"
    DISPLAY_NAME_EN = "Boolean Logic"
    DESCRIPTION_ZH = "对两个布尔值执行逻辑运算。"
    DESCRIPTION_EN = "Runs boolean logic against two inputs."
    ICON_NAME = "logic"
    DATA_INPUT_SPECS = (
        DataPortSpec("left", "左布尔", "bool", "左侧布尔值"),
        DataPortSpec("right", "右布尔", "bool", "右侧布尔值"),
    )
    DATA_OUTPUT_SPECS = (
        DataPortSpec("result", "逻辑结果", "bool", "逻辑运算结果", multi_connection=True),
    )
    FIELD_SPECS = (
        bool_field("left", True, "左布尔", "Left", "未连线时使用的左布尔值。", "Fallback left boolean."),
        enum_field(
            "operator",
            "and",
            "逻辑符",
            "Operator",
            "布尔逻辑运算符。",
            "Boolean operator.",
            ("and", "or", "xor"),
        ),
        bool_field("right", True, "右布尔", "Right", "未连线时使用的右布尔值。", "Fallback right boolean."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        left = self.resolve_data_input_value(context, "left", as_bool(self.get_property("left")))
        right = self.resolve_data_input_value(context, "right", as_bool(self.get_property("right")))
        operator = self.field_value("operator")
        result = {"and": left and right, "or": left or right, "xor": bool(left) ^ bool(right)}[operator]
        context.set_port_value(self.id, "result", result)
        context.last_result = result
        return RuntimeEvent(summary="boolean_logic", payload=result, next_flow_key=FLOW_OUT, output_values={"result": result})

    def emit_python(self, export_context: Any) -> list[str]:
        operator = self.field_value("operator")
        source_left = self.connected_data_source("left")
        source_right = self.connected_data_source("right")
        fallback_left = as_bool(self.get_property("left"))
        fallback_right = as_bool(self.get_property("right"))
        expr = {"and": "left_value and right_value", "or": "left_value or right_value", "xor": "bool(left_value) ^ bool(right_value)"}[
            operator
        ]
        return [
            f"left_value = as_bool(_read_input_value(context, {repr((source_left[0].id, source_left[1])) if source_left else 'None'}, {fallback_left!r}))",
            f"right_value = as_bool(_read_input_value(context, {repr((source_right[0].id, source_right[1])) if source_right else 'None'}, {fallback_right!r}))",
            f"logic_result = {expr}",
            f"_set_output_value(context, {self.id!r}, 'result', logic_result)",
            "context['last_result'] = logic_result",
            "return 'flow_out'",
        ]


class BooleanNotNode(GeneralLogicNode):
    NODE_NAME = "布尔非"
    DISPLAY_NAME_ZH = "布尔非"
    DISPLAY_NAME_EN = "Boolean Not"
    DESCRIPTION_ZH = "对一个布尔值取反。"
    DESCRIPTION_EN = "Negates a boolean input."
    ICON_NAME = "logic"
    DATA_INPUT_SPECS = (
        DataPortSpec("value", "输入布尔", "bool", "输入布尔值"),
    )
    DATA_OUTPUT_SPECS = (
        DataPortSpec("result", "取反结果", "bool", "取反结果", multi_connection=True),
    )
    FIELD_SPECS = (
        bool_field("value", True, "输入布尔", "Value", "未连线时使用的布尔值。", "Fallback boolean value."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = self.resolve_data_input_value(context, "value", as_bool(self.get_property("value")))
        result = not value
        context.set_port_value(self.id, "result", result)
        context.last_result = result
        return RuntimeEvent(summary="boolean_not", payload=result, next_flow_key=FLOW_OUT, output_values={"result": result})

    def emit_python(self, export_context: Any) -> list[str]:
        source = self.connected_data_source("value")
        fallback = as_bool(self.get_property("value"))
        return [
            f"bool_value = as_bool(_read_input_value(context, {repr((source[0].id, source[1])) if source else 'None'}, {fallback!r}))",
            "not_result = not bool_value",
            f"_set_output_value(context, {self.id!r}, 'result', not_result)",
            "context['last_result'] = not_result",
            "return 'flow_out'",
        ]


class ReadTextVariableNode(GeneralValueNode):
    NODE_NAME = "读取文本变量"
    DISPLAY_NAME_ZH = "读取文本变量"
    DISPLAY_NAME_EN = "Read Text Variable"
    DESCRIPTION_ZH = "从变量上下文读取文本值。"
    DESCRIPTION_EN = "Reads a text value from the variable context."
    ICON_NAME = "variable"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "变量值", "str", "读取到的文本变量", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("variable_name", "result", "变量名", "Variable Name", "要读取的变量名。", "Variable name to read.", required=True),
        text_field("default_value", "", "默认值", "Default", "变量缺失时返回的默认值。", "Default value when variable is missing."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_text(context.variables.get(self.field_value("variable_name"), self.field_value("default_value")))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="read_text_variable", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        return [
            f"variable_value = as_text(context['variables'].get({self.field_value('variable_name')!r}, {self.field_value('default_value')!r}))",
            f"_set_output_value(context, {self.id!r}, 'value', variable_value)",
            "context['last_result'] = variable_value",
            "return 'flow_out'",
        ]


class ReadBoolVariableNode(GeneralValueNode):
    NODE_NAME = "读取布尔变量"
    DISPLAY_NAME_ZH = "读取布尔变量"
    DISPLAY_NAME_EN = "Read Bool Variable"
    DESCRIPTION_ZH = "从变量上下文读取布尔值。"
    DESCRIPTION_EN = "Reads a boolean value from the variable context."
    ICON_NAME = "variable"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "变量值", "bool", "读取到的布尔变量", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("variable_name", "flag", "变量名", "Variable Name", "要读取的变量名。", "Variable name to read.", required=True),
        bool_field("default_value", False, "默认值", "Default", "变量缺失时返回的默认值。", "Default value when variable is missing."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_bool(context.variables.get(self.field_value("variable_name"), as_bool(self.get_property("default_value"))))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="read_bool_variable", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        default_value = as_bool(self.get_property("default_value"))
        return [
            f"variable_value = as_bool(context['variables'].get({self.field_value('variable_name')!r}, {default_value!r}))",
            f"_set_output_value(context, {self.id!r}, 'value', variable_value)",
            "context['last_result'] = variable_value",
            "return 'flow_out'",
        ]


class ReadIntVariableNode(GeneralValueNode):
    NODE_NAME = "读取整数变量"
    DISPLAY_NAME_ZH = "读取整数变量"
    DISPLAY_NAME_EN = "Read Int Variable"
    DESCRIPTION_ZH = "从变量上下文读取整数值。"
    DESCRIPTION_EN = "Reads an integer value from the variable context."
    ICON_NAME = "variable"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "变量值", "int", "读取到的整数变量", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("variable_name", "counter", "变量名", "Variable Name", "要读取的变量名。", "Variable name to read.", required=True),
        int_field("default_value", 0, "默认值", "Default", "变量缺失时返回的默认值。", "Default value when variable is missing."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_int(context.variables.get(self.field_value("variable_name"), as_int(self.get_property("default_value"))))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="read_int_variable", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        default_value = as_int(self.get_property("default_value"))
        return [
            f"variable_value = as_int(context['variables'].get({self.field_value('variable_name')!r}, {default_value!r}))",
            f"_set_output_value(context, {self.id!r}, 'value', variable_value)",
            "context['last_result'] = variable_value",
            "return 'flow_out'",
        ]


class ReadFloatVariableNode(GeneralValueNode):
    NODE_NAME = "读取浮点变量"
    DISPLAY_NAME_ZH = "读取浮点变量"
    DISPLAY_NAME_EN = "Read Float Variable"
    DESCRIPTION_ZH = "从变量上下文读取浮点值。"
    DESCRIPTION_EN = "Reads a float value from the variable context."
    ICON_NAME = "variable"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "变量值", "float", "读取到的浮点变量", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("variable_name", "ratio", "变量名", "Variable Name", "要读取的变量名。", "Variable name to read.", required=True),
        float_field("default_value", 0.0, "默认值", "Default", "变量缺失时返回的默认值。", "Default value when variable is missing."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        value = as_float(context.variables.get(self.field_value("variable_name"), as_float(self.get_property("default_value"))))
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="read_float_variable", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        default_value = as_float(self.get_property("default_value"))
        return [
            f"variable_value = as_float(context['variables'].get({self.field_value('variable_name')!r}, {default_value!r}))",
            f"_set_output_value(context, {self.id!r}, 'value', variable_value)",
            "context['last_result'] = variable_value",
            "return 'flow_out'",
        ]


class WriteVariableFromInputNode(GeneralValueNode):
    NODE_NAME = "写回变量"
    DISPLAY_NAME_ZH = "写回变量"
    DISPLAY_NAME_EN = "Write Variable From Input"
    DESCRIPTION_ZH = "把输入数据原样写回到变量上下文。"
    DESCRIPTION_EN = "Writes an incoming value back into the variable context."
    ICON_NAME = "variable"
    DATA_INPUT_SPECS = (
        DataPortSpec("value", "输入值", "any", "待写回的输入值"),
    )
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "变量值", "any", "写回后的变量值", multi_connection=True),
    )
    FIELD_SPECS = (
        text_field("variable_name", "result", "变量名", "Variable Name", "写回目标变量名。", "Variable name to write.", required=True),
        text_field("fallback_value", "", "回退值", "Fallback", "未连线时写回的默认值。", "Fallback value when no input is connected."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        source = self.connected_data_source("value")
        if source is not None:
            source_node, source_key = source
            value = context.get_port_value(source_node.id, source_key)
        else:
            value = self.get_property("fallback_value")
        context.variables[self.field_value("variable_name")] = value
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="write_variable_from_input", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        source = self.connected_data_source("value")
        return [
            f"input_value = _read_input_value(context, {repr((source[0].id, source[1])) if source else 'None'}, {self.get_property('fallback_value')!r})",
            f"context['variables'][{self.field_value('variable_name')!r}] = input_value",
            f"_set_output_value(context, {self.id!r}, 'value', input_value)",
            "context['last_result'] = input_value",
            "return 'flow_out'",
        ]


class LastResultIndexNode(GeneralValueNode):
    NODE_NAME = "结果拆包"
    DISPLAY_NAME_ZH = "结果拆包"
    DISPLAY_NAME_EN = "Unpack Last Result"
    DESCRIPTION_ZH = "从 last_result 的列表/元组中按索引提取一个元素。"
    DESCRIPTION_EN = "Extracts one element from last_result when it is a list or tuple."
    ICON_NAME = "constant"
    DATA_OUTPUT_SPECS = (
        DataPortSpec("value", "拆包值", "any", "按索引提取的结果值", multi_connection=True),
    )
    FIELD_SPECS = (
        int_field("index", 0, "索引", "Index", "要提取的结果索引。", "Result index to extract."),
        text_field("default_value", "", "默认值", "Default", "last_result 不可拆包时的默认值。", "Default when last_result is not indexable."),
    )

    def execute(self, context: Any) -> RuntimeEvent:
        default_value = self.get_property("default_value")
        value = default_value
        if isinstance(context.last_result, (list, tuple)):
            index = as_int(self.get_property("index"))
            if 0 <= index < len(context.last_result):
                value = context.last_result[index]
        context.set_port_value(self.id, "value", value)
        context.last_result = value
        return RuntimeEvent(summary="unpack_last_result", payload=value, next_flow_key=FLOW_OUT, output_values={"value": value})

    def emit_python(self, export_context: Any) -> list[str]:
        index = as_int(self.get_property("index"))
        default_value = self.get_property("default_value")
        return [
            f"unpacked_value = {default_value!r}",
            "if isinstance(context.get('last_result'), (list, tuple)):",
            f"    if 0 <= {index} < len(context['last_result']):",
            f"        unpacked_value = context['last_result'][{index}]",
            f"_set_output_value(context, {self.id!r}, 'value', unpacked_value)",
            "context['last_result'] = unpacked_value",
            "return 'flow_out'",
        ]


class SignalGeneratorNode(InstrumentNode):
    CATEGORY_ZH = "信号发生器"
    CATEGORY_EN = "Signal Generator"
    SESSION_KIND = "signal_generator"
    API_MODULE = "Instruments_pythonic.signal_generator"
    API_CLASS_NAME = "SimSignalGeneratorIvi"
    ICON_NAME = "signal"


class OpenSignalGeneratorSessionNode(OpenInstrumentSessionNode, SignalGeneratorNode):
    NODE_NAME = "打开信号发生器会话"
    DISPLAY_NAME_ZH = "打开会话"
    DISPLAY_NAME_EN = "Open Session"
    DESCRIPTION_ZH = "创建并初始化信号发生器会话。"
    DESCRIPTION_EN = "Creates and initializes a signal generator session."
    API_CLASS = SimSignalGeneratorIvi
    FIELD_SPECS = (
        session_name_field("sg_main"),
        resource_name_field("TCPIP0::192.168.0.10::INSTR"),
        bool_field("id_query", True, "执行 ID 查询", "ID Query", "初始化后读取设备标识。", "Read device identity after initialize."),
        bool_field("reset", False, "初始化时复位", "Reset On Open", "打开时是否执行 reset。", "Whether to reset during open."),
    )


class QuerySignalGeneratorIdentityNode(SessionMethodNode, SignalGeneratorNode):
    NODE_NAME = "查询信号发生器标识"
    DISPLAY_NAME_ZH = "查询标识"
    DISPLAY_NAME_EN = "Query Identity"
    DESCRIPTION_ZH = "读取信号发生器身份字符串。"
    DESCRIPTION_EN = "Reads the signal generator identity string."
    METHOD_NAME = "get_identity"
    METHOD_ARG_FIELDS = ()
    RESULT_TO_VARIABLE = True
    FIELD_SPECS = (
        session_name_field("sg_main"),
        save_as_field("sg_identity"),
    )


class ResetSignalGeneratorNode(SessionMethodNode, SignalGeneratorNode):
    NODE_NAME = "复位信号发生器"
    DISPLAY_NAME_ZH = "复位"
    DISPLAY_NAME_EN = "Reset"
    DESCRIPTION_ZH = "复位信号发生器。"
    DESCRIPTION_EN = "Resets the signal generator."
    METHOD_NAME = "reset"
    METHOD_ARG_FIELDS = ()
    FIELD_SPECS = (session_name_field("sg_main"),)


class ConfigureSignalGeneratorWaveformNode(SessionMethodNode, SignalGeneratorNode):
    NODE_NAME = "配置波形"
    DISPLAY_NAME_ZH = "配置波形"
    DISPLAY_NAME_EN = "Configure Waveform"
    DESCRIPTION_ZH = "设置波形类型、频率、幅值、偏置和相位。"
    DESCRIPTION_EN = "Configures waveform type, frequency, amplitude, offset, and phase."
    METHOD_NAME = "configure_waveform"
    METHOD_ARG_FIELDS = ("channel", "waveform", "frequency", "amplitude", "offset", "phase")
    FIELD_SPECS = (
        session_name_field("sg_main"),
        channel_field("CH1"),
        enum_field("waveform", "SINE", "波形", "Waveform", "输出波形类型。", "Output waveform type.", ("SINE", "SQUARE", "TRIANGLE", "PULSE")),
        float_field("frequency", 1000.0, "频率(Hz)", "Frequency (Hz)", "输出频率。", "Output frequency."),
        float_field("amplitude", 1.0, "幅值(Vpp)", "Amplitude (Vpp)", "输出幅值。", "Output amplitude."),
        float_field("offset", 0.0, "偏置(V)", "Offset (V)", "直流偏置。", "DC offset.", required=False),
        float_field("phase", 0.0, "相位(度)", "Phase (deg)", "输出相位。", "Output phase.", required=False),
    )


class SignalGeneratorOutputEnableNode(SessionMethodNode, SignalGeneratorNode):
    NODE_NAME = "设置输出开关"
    DISPLAY_NAME_ZH = "输出开关"
    DISPLAY_NAME_EN = "Output Enable"
    DESCRIPTION_ZH = "开启或关闭指定通道输出。"
    DESCRIPTION_EN = "Enables or disables the specified channel output."
    METHOD_NAME = "configure_output"
    METHOD_ARG_FIELDS = ("channel", "enabled")
    FIELD_SPECS = (
        session_name_field("sg_main"),
        channel_field("CH1"),
        bool_field("enabled", True, "使能输出", "Enabled", "是否打开输出。", "Whether output is enabled."),
    )


class CloseSignalGeneratorSessionNode(CloseSessionNode, SignalGeneratorNode):
    NODE_NAME = "关闭信号发生器会话"
    DISPLAY_NAME_ZH = "关闭会话"
    DISPLAY_NAME_EN = "Close Session"
    DESCRIPTION_ZH = "关闭信号发生器会话。"
    DESCRIPTION_EN = "Closes the signal generator session."
    FIELD_SPECS = (session_name_field("sg_main"),)


class DigitalPatternNode(InstrumentNode):
    CATEGORY_ZH = "数字模式发生器"
    CATEGORY_EN = "Digital Pattern Generator"
    SESSION_KIND = "digital_pattern_generator"
    API_MODULE = "Instruments_pythonic.digital_pattern_generator"
    API_CLASS_NAME = "SimDigitalPatternGeneratorIvi"
    ICON_NAME = "pattern"


class OpenDigitalPatternSessionNode(OpenInstrumentSessionNode, DigitalPatternNode):
    NODE_NAME = "打开数字模式发生器会话"
    DISPLAY_NAME_ZH = "打开会话"
    DISPLAY_NAME_EN = "Open Session"
    DESCRIPTION_ZH = "创建并初始化数字模式发生器会话。"
    DESCRIPTION_EN = "Creates and initializes the digital pattern generator session."
    API_CLASS = SimDigitalPatternGeneratorIvi
    FIELD_SPECS = (
        session_name_field("dpg_main"),
        resource_name_field("PXI0::20-0.0::INSTR"),
        bool_field("id_query", True, "执行 ID 查询", "ID Query", "初始化后读取设备标识。", "Read device identity after initialize."),
        bool_field("reset", False, "初始化时复位", "Reset On Open", "打开时是否执行 reset。", "Whether to reset during open."),
    )


class QueryDigitalPatternIdentityNode(SessionMethodNode, DigitalPatternNode):
    NODE_NAME = "查询数字模式发生器标识"
    DISPLAY_NAME_ZH = "查询标识"
    DISPLAY_NAME_EN = "Query Identity"
    DESCRIPTION_ZH = "读取数字模式发生器身份字符串。"
    DESCRIPTION_EN = "Reads the digital pattern generator identity string."
    METHOD_NAME = "get_identity"
    METHOD_ARG_FIELDS = ()
    RESULT_TO_VARIABLE = True
    FIELD_SPECS = (
        session_name_field("dpg_main"),
        save_as_field("dpg_identity"),
    )


class ResetDigitalPatternNode(SessionMethodNode, DigitalPatternNode):
    NODE_NAME = "复位数字模式发生器"
    DISPLAY_NAME_ZH = "复位"
    DISPLAY_NAME_EN = "Reset"
    DESCRIPTION_ZH = "复位数字模式发生器。"
    DESCRIPTION_EN = "Resets the digital pattern generator."
    METHOD_NAME = "reset"
    METHOD_ARG_FIELDS = ()
    FIELD_SPECS = (session_name_field("dpg_main"),)


class ConfigureDigitalTimingNode(SessionMethodNode, DigitalPatternNode):
    NODE_NAME = "配置时序"
    DISPLAY_NAME_ZH = "配置时序"
    DISPLAY_NAME_EN = "Configure Timing"
    DESCRIPTION_ZH = "设置采样率和逻辑电平。"
    DESCRIPTION_EN = "Configures sample rate and logic level."
    METHOD_NAME = "configure_timing"
    METHOD_ARG_FIELDS = ("sample_rate", "logic_level")
    FIELD_SPECS = (
        session_name_field("dpg_main"),
        float_field("sample_rate", 1_000_000.0, "采样率(Hz)", "Sample Rate (Hz)", "数字输出采样率。", "Digital output sample rate."),
        enum_field("logic_level", "3.3V", "逻辑电平", "Logic Level", "逻辑输出电平。", "Logic output level.", ("1.8V", "2.5V", "3.3V", "5V")),
    )


class LoadDigitalPatternNode(SessionMethodNode, DigitalPatternNode):
    NODE_NAME = "加载模式"
    DISPLAY_NAME_ZH = "加载模式"
    DISPLAY_NAME_EN = "Load Pattern"
    DESCRIPTION_ZH = "加载要输出的数字模式。"
    DESCRIPTION_EN = "Loads the digital pattern to output."
    METHOD_NAME = "load_pattern"
    METHOD_ARG_FIELDS = ("pattern_name", "pattern_bits", "loop_count")
    FIELD_SPECS = (
        session_name_field("dpg_main"),
        text_field("pattern_name", "burst_A", "模式名", "Pattern Name", "模式名称。", "Pattern name.", required=True),
        text_field("pattern_bits", "101100111000", "模式比特", "Pattern Bits", "比特串或模式文本。", "Bit string or pattern text.", required=True, multiline=True),
        int_field("loop_count", 1, "循环次数", "Loop Count", "模式循环次数。", "Pattern loop count."),
    )


class StartDigitalOutputNode(SessionMethodNode, DigitalPatternNode):
    NODE_NAME = "开始输出"
    DISPLAY_NAME_ZH = "开始输出"
    DISPLAY_NAME_EN = "Start Output"
    DESCRIPTION_ZH = "启动数字模式输出。"
    DESCRIPTION_EN = "Starts digital pattern output."
    METHOD_NAME = "start_output"
    METHOD_ARG_FIELDS = ()
    FIELD_SPECS = (session_name_field("dpg_main"),)


class StopDigitalOutputNode(SessionMethodNode, DigitalPatternNode):
    NODE_NAME = "停止输出"
    DISPLAY_NAME_ZH = "停止输出"
    DISPLAY_NAME_EN = "Stop Output"
    DESCRIPTION_ZH = "停止数字模式输出。"
    DESCRIPTION_EN = "Stops digital pattern output."
    METHOD_NAME = "stop_output"
    METHOD_ARG_FIELDS = ()
    FIELD_SPECS = (session_name_field("dpg_main"),)


class CloseDigitalPatternSessionNode(CloseSessionNode, DigitalPatternNode):
    NODE_NAME = "关闭数字模式发生器会话"
    DISPLAY_NAME_ZH = "关闭会话"
    DISPLAY_NAME_EN = "Close Session"
    DESCRIPTION_ZH = "关闭数字模式发生器会话。"
    DESCRIPTION_EN = "Closes the digital pattern generator session."
    FIELD_SPECS = (session_name_field("dpg_main"),)


class MultiSerialCardNode(InstrumentNode):
    CATEGORY_ZH = "多通道串口卡"
    CATEGORY_EN = "Multi Serial Card"
    SESSION_KIND = "multi_serial_card"
    API_MODULE = "Instruments_pythonic.multi_serial_card"
    API_CLASS_NAME = "SimMultiSerialCardIvi"
    ICON_NAME = "serial"


class OpenMultiSerialCardSessionNode(OpenInstrumentSessionNode, MultiSerialCardNode):
    NODE_NAME = "打开串口卡会话"
    DISPLAY_NAME_ZH = "打开会话"
    DISPLAY_NAME_EN = "Open Session"
    DESCRIPTION_ZH = "创建并初始化多通道串口卡会话。"
    DESCRIPTION_EN = "Creates and initializes the multi serial card session."
    API_CLASS = SimMultiSerialCardIvi
    FIELD_SPECS = (
        session_name_field("serial_main"),
        resource_name_field("PCI::SERIAL-CARD-01"),
        bool_field("id_query", True, "执行 ID 查询", "ID Query", "初始化后读取设备标识。", "Read device identity after initialize."),
        bool_field("reset", False, "初始化时复位", "Reset On Open", "打开时是否执行 reset。", "Whether to reset during open."),
    )


class OpenSerialPortNode(SessionMethodNode, MultiSerialCardNode):
    NODE_NAME = "打开端口"
    DISPLAY_NAME_ZH = "打开端口"
    DISPLAY_NAME_EN = "Open Port"
    DESCRIPTION_ZH = "打开指定通道对应的串口。"
    DESCRIPTION_EN = "Opens the serial port for the selected channel."
    METHOD_NAME = "open_port"
    METHOD_ARG_FIELDS = ("channel", "port_name", "baud_rate", "data_bits", "parity", "stop_bits", "timeout")
    FIELD_SPECS = (
        session_name_field("serial_main"),
        channel_field("CH1"),
        text_field("port_name", "COM1", "端口名", "Port Name", "串口名称。", "Serial port name.", required=True),
        int_field("baud_rate", 115200, "波特率", "Baud Rate", "串口波特率。", "Serial baud rate."),
        int_field("data_bits", 8, "数据位", "Data Bits", "串口数据位。", "Serial data bits."),
        enum_field("parity", "N", "校验位", "Parity", "串口校验位。", "Serial parity.", ("N", "E", "O")),
        int_field("stop_bits", 1, "停止位", "Stop Bits", "串口停止位。", "Serial stop bits."),
        float_field("timeout", 1.0, "超时(秒)", "Timeout (s)", "端口超时设置。", "Port timeout setting."),
    )


class WriteSerialNode(SessionMethodNode, MultiSerialCardNode):
    NODE_NAME = "写串口"
    DISPLAY_NAME_ZH = "写串口"
    DISPLAY_NAME_EN = "Write"
    DESCRIPTION_ZH = "向串口写入数据。"
    DESCRIPTION_EN = "Writes data to the serial channel."
    METHOD_NAME = "write"
    METHOD_ARG_FIELDS = ("channel", "data", "encoding")
    FIELD_SPECS = (
        session_name_field("serial_main"),
        channel_field("CH1"),
        text_field("data", "*IDN?", "写入数据", "Data", "要写入的串口文本。", "Serial text to write.", required=True, multiline=True),
        text_field("encoding", "utf-8", "编码", "Encoding", "字符串编码。", "String encoding.", required=True),
    )


class ReadSerialNode(SessionMethodNode, MultiSerialCardNode):
    NODE_NAME = "读串口"
    DISPLAY_NAME_ZH = "读串口"
    DISPLAY_NAME_EN = "Read"
    DESCRIPTION_ZH = "从串口读取数据并保存到变量。"
    DESCRIPTION_EN = "Reads serial data and stores it into a variable."
    METHOD_NAME = "read"
    METHOD_ARG_FIELDS = ("channel", "size", "timeout")
    RESULT_TO_VARIABLE = True
    FIELD_SPECS = (
        session_name_field("serial_main"),
        channel_field("CH1"),
        int_field("size", 0, "读取长度", "Read Size", "0 表示读取全部缓冲内容。", "0 means read full buffer.", required=False),
        float_field("timeout", 1.0, "超时(秒)", "Timeout (s)", "读超时。", "Read timeout.", required=False),
        save_as_field("serial_reply"),
    )


class CloseSerialPortNode(SessionMethodNode, MultiSerialCardNode):
    NODE_NAME = "关闭端口"
    DISPLAY_NAME_ZH = "关闭端口"
    DISPLAY_NAME_EN = "Close Port"
    DESCRIPTION_ZH = "关闭指定通道对应的串口。"
    DESCRIPTION_EN = "Closes the serial port for the selected channel."
    METHOD_NAME = "close_port"
    METHOD_ARG_FIELDS = ("channel",)
    FIELD_SPECS = (
        session_name_field("serial_main"),
        channel_field("CH1"),
    )


class CloseMultiSerialCardSessionNode(CloseSessionNode, MultiSerialCardNode):
    NODE_NAME = "关闭串口卡会话"
    DISPLAY_NAME_ZH = "关闭会话"
    DISPLAY_NAME_EN = "Close Session"
    DESCRIPTION_ZH = "关闭多通道串口卡会话。"
    DESCRIPTION_EN = "Closes the multi serial card session."
    FIELD_SPECS = (session_name_field("serial_main"),)


ALL_NODE_CLASSES = [
    StartNode,
    CommentNode,
    DelayNode,
    SetVariableNode,
    ReturnNode,
    RaiseErrorNode,
    BooleanConstantNode,
    IntegerConstantNode,
    FloatConstantNode,
    TextConstantNode,
    MathBinaryNode,
    CompareNumberNode,
    CompareTextNode,
    BooleanLogicNode,
    BooleanNotNode,
    WriteVariableFromInputNode,
    LastResultIndexNode,
    ReadTextVariableNode,
    ReadBoolVariableNode,
    ReadIntVariableNode,
    ReadFloatVariableNode,
    OpenSignalGeneratorSessionNode,
    QuerySignalGeneratorIdentityNode,
    ResetSignalGeneratorNode,
    ConfigureSignalGeneratorWaveformNode,
    SignalGeneratorOutputEnableNode,
    CloseSignalGeneratorSessionNode,
    OpenDigitalPatternSessionNode,
    QueryDigitalPatternIdentityNode,
    ResetDigitalPatternNode,
    ConfigureDigitalTimingNode,
    LoadDigitalPatternNode,
    StartDigitalOutputNode,
    StopDigitalOutputNode,
    CloseDigitalPatternSessionNode,
    OpenMultiSerialCardSessionNode,
    OpenSerialPortNode,
    WriteSerialNode,
    ReadSerialNode,
    CloseSerialPortNode,
    CloseMultiSerialCardSessionNode,
]

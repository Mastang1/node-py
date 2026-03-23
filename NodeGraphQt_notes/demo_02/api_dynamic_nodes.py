from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import pkgutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .common import GENERATED_DIR, FieldSpec, as_bool, as_float, as_int, as_text, ensure_directory
from .nodes import DataPortSpec, FlowPortSpec, RuntimeEvent, WorkflowNode

_CATEGORY_RGB: dict[str, tuple[int, int, int]] = {
    "signal generator": (43, 108, 176),
    "digital pattern generator": (92, 88, 172),
    "multi serial card": (58, 124, 98),
    "general flow": (128, 86, 158),
    "general": (78, 88, 104),
}


def _rgb_for_category(category_en: str) -> tuple[int, int, int]:
    key = (category_en or "").strip().lower()
    return _CATEGORY_RGB.get(key, (62, 92, 128))


@dataclass(frozen=True)
class MethodParamMeta:
    name: str
    zh: str
    param_type: str
    required: bool
    default: Any
    tooltip: str
    options: tuple[str, ...]


@dataclass(frozen=True)
class MethodReturnMeta:
    name: str
    zh: str
    return_type: str
    tooltip: str


@dataclass(frozen=True)
class MethodFlowPortMeta:
    key: str
    zh: str


@dataclass(frozen=True)
class ApiMethodMeta:
    module_name: str
    class_name: str
    method_name: str
    func_desc: str
    node_name_zh: str
    node_name_en: str
    category_zh: str
    category_en: str
    icon_name: str
    control_kind: str
    flow_outputs: tuple[MethodFlowPortMeta, ...]
    params: tuple[MethodParamMeta, ...]
    returns: tuple[MethodReturnMeta, ...]

    @property
    def registry_key(self) -> str:
        safe_module = self.module_name.replace(".", "_")
        safe_method = self.method_name.replace(".", "_")
        return f"{safe_module}__{self.class_name}__{safe_method}"

    @property
    def node_identifier(self) -> str:
        return f"demo02.api.{self.registry_key}"

    @property
    def export_module_name(self) -> str:
        """Import path when ``sys.path`` contains the ``demo_02`` package root only."""
        prefix = "demo_02."
        if self.module_name.startswith(prefix):
            return self.module_name[len(prefix) :]
        return self.module_name

    @property
    def dynamic_class_name(self) -> str:
        safe_method = self.method_name.replace("_", "").title()
        safe_class = self.class_name.replace("_", "")
        return f"ApiNode{safe_class}{safe_method}"

    @property
    def instance_key(self) -> str:
        return f"{self.module_name}:{self.class_name}"

    @property
    def is_control_node(self) -> bool:
        return bool(self.control_kind)


def _kind_for_param_type(param_type: str) -> str:
    if param_type in {"int", "float", "bool", "enum"}:
        return param_type
    if param_type in {"handle", "var_ref"}:
        return "str"
    return "str"


def _field_specs_from_meta(meta: ApiMethodMeta) -> tuple[FieldSpec, ...]:
    fields: list[FieldSpec] = []
    for param in meta.params:
        kind = _kind_for_param_type(param.param_type)
        fields.append(
            FieldSpec(
                name=param.name,
                kind=kind,
                default=param.default,
                label_zh=param.zh,
                label_en=param.name,
                tooltip_zh=param.tooltip,
                tooltip_en=param.tooltip,
                required=param.required,
                options=param.options,
            )
        )
    if meta.returns and not meta.is_control_node:
        fields.append(
            FieldSpec(
                name="save_prefix",
                kind="str",
                default=meta.method_name,
                label_zh="返回值前缀",
                label_en="Return Prefix",
                tooltip_zh="返回值写入 context['variables'] 时使用的前缀。",
                tooltip_en="Prefix used when storing return values into context['variables'].",
                required=False,
            )
        )
    return tuple(fields)


def _data_input_specs_from_meta(meta: ApiMethodMeta) -> tuple[DataPortSpec, ...]:
    return tuple(
        DataPortSpec(
            key=param.name,
            label=param.zh or param.name,
            data_type=param.param_type,
            tooltip=param.tooltip,
            required=param.required,
        )
        for param in meta.params
    )


def _data_output_specs_from_meta(meta: ApiMethodMeta) -> tuple[DataPortSpec, ...]:
    return tuple(
        DataPortSpec(
            key=ret.name,
            label=ret.zh or ret.name,
            data_type=ret.return_type,
            tooltip=ret.tooltip,
            multi_connection=True,
        )
        for ret in meta.returns
    )


def _flow_input_specs_from_meta(meta: ApiMethodMeta) -> tuple[FlowPortSpec, ...]:
    allow_multi_input = meta.control_kind in {"while_loop", "for_range"}
    return (FlowPortSpec("flow_in", "flow_in", False, allow_multi_input),)


def _flow_output_specs_from_meta(meta: ApiMethodMeta) -> tuple[FlowPortSpec, ...]:
    if meta.flow_outputs:
        return tuple(
            FlowPortSpec(key=port.key, label=port.zh or port.key, display_name=True, multi_connection=False)
            for port in meta.flow_outputs
        )
    return WorkflowNode.FLOW_OUTPUT_SPECS


class DynamicApiMethodNode(WorkflowNode):
    API_META: ApiMethodMeta | None = None
    FIELD_SPECS: tuple[FieldSpec, ...] = ()
    DATA_INPUT_SPECS: tuple[DataPortSpec, ...] = ()
    DATA_OUTPUT_SPECS: tuple[DataPortSpec, ...] = ()
    FLOW_OUTPUT_SPECS: tuple[FlowPortSpec, ...] = WorkflowNode.FLOW_OUTPUT_SPECS

    @classmethod
    def _api_meta(cls) -> ApiMethodMeta:
        if cls.API_META is None:
            raise RuntimeError("API_META is missing for dynamic API node.")
        return cls.API_META

    @classmethod
    def display_name(cls, language: str = "zh") -> str:
        meta = cls._api_meta()
        return meta.node_name_zh if language == "zh" else meta.node_name_en

    @classmethod
    def category_name(cls, language: str = "zh") -> str:
        meta = cls._api_meta()
        return meta.category_zh if language == "zh" else meta.category_en

    @classmethod
    def description(cls, language: str = "zh") -> str:
        return cls._api_meta().func_desc

    def _coerce_value(self, value: Any, param_type: str) -> Any:
        if param_type == "bool":
            return as_bool(value)
        if param_type == "int":
            return as_int(value)
        if param_type == "float":
            return as_float(value)
        if param_type in {"handle", "var_ref"}:
            key = as_text(value)
            return key
        return as_text(value)

    def _resolve_property_value(self, context: Any, param: MethodParamMeta) -> Any:
        value = self.get_property(param.name)
        if param.param_type in {"handle", "var_ref"}:
            key = as_text(value)
            return context.variables.get(key, key)
        return self._coerce_value(value, param.param_type)

    def _resolve_param_value(self, context: Any, param: MethodParamMeta) -> Any:
        source = self.connected_data_source(param.name)
        if source is not None:
            source_node, source_key = source
            value = context.get_port_value(source_node.id, source_key)
            if param.param_type in {"handle", "var_ref"}:
                key = as_text(value)
                return context.variables.get(key, key)
            return self._coerce_value(value, param.param_type)
        return self._resolve_property_value(context, param)

    def _instance_var_name(self, export_context: Any, meta: ApiMethodMeta) -> str:
        return export_context.session_var(meta.instance_key.replace(":", "_"))

    @staticmethod
    def _normalize_results(result: Any) -> list[Any]:
        if result is None:
            return []
        if isinstance(result, (list, tuple)):
            return list(result)
        return [result]

    def _write_results_to_context(self, context: Any, meta: ApiMethodMeta, results: list[Any]) -> None:
        prefix = as_text(self.get_property("save_prefix"), meta.method_name)
        for index, ret in enumerate(meta.returns):
            value = results[index] if index < len(results) else None
            context.set_port_value(self.id, ret.name, value)
            context.variables[ret.name] = value
            context.variables[f"{prefix}.{ret.name}"] = value
        if not meta.returns:
            context.last_result = results if len(results) != 1 else results[0] if results else None
            return
        if len(results) == 1:
            context.last_result = results[0]
        else:
            context.last_result = results

    def _execute_control_node(self, context: Any, meta: ApiMethodMeta, kwargs: dict[str, Any]) -> RuntimeEvent:
        control_kind = meta.control_kind

        if control_kind in {"if_branch", "elif_branch"}:
            previous_matched = as_bool(kwargs.get("previous_matched")) if "previous_matched" in kwargs else False
            condition = as_bool(kwargs.get("condition"))
            matched = condition if control_kind == "if_branch" else (not previous_matched and condition)
            true_value = kwargs.get("true_value", kwargs.get("value", ""))
            false_value = kwargs.get("false_value", "")
            selected = true_value if matched else false_value
            payload = {"selected": selected, "matched": matched}
            next_flow_key = "true_branch" if matched else "false_branch"
            context.last_result = selected
            return RuntimeEvent(
                summary=meta.method_name,
                payload=payload,
                next_flow_key=next_flow_key,
                output_values=payload,
            )

        if control_kind == "else_branch":
            previous_matched = as_bool(kwargs.get("previous_matched"))
            selected = "" if previous_matched else kwargs.get("value", "")
            next_flow_key = "skipped" if previous_matched else "else_branch"
            context.last_result = selected
            return RuntimeEvent(
                summary=meta.method_name,
                payload={"selected": selected},
                next_flow_key=next_flow_key,
                output_values={"selected": selected},
            )

        if control_kind == "while_loop":
            state = context.loop_states.setdefault(self.id, {"count": 0})
            condition = as_bool(kwargs.get("condition"))
            max_iterations = max(0, as_int(kwargs.get("max_iterations"), 10))
            if condition and state["count"] < max_iterations:
                state["count"] += 1
                current_count = state["count"]
                context.last_result = current_count
                return RuntimeEvent(
                    summary=meta.method_name,
                    payload={"iterations": current_count},
                    next_flow_key="loop_body",
                    output_values={"iterations": current_count},
                )
            total = state.get("count", 0)
            state["count"] = 0
            context.last_result = total
            return RuntimeEvent(
                summary=meta.method_name,
                payload={"iterations": total},
                next_flow_key="completed",
                output_values={"iterations": total},
            )

        if control_kind == "for_range":
            state = context.loop_states.setdefault(self.id, {"index": 0})
            total = max(0, as_int(kwargs.get("value"), 0))
            if state["index"] < total:
                current_value = state["index"]
                state["index"] += 1
                output_values: dict[str, Any] = {}
                if meta.returns:
                    output_values[meta.returns[0].name] = current_value
                if len(meta.returns) > 1:
                    output_values[meta.returns[1].name] = current_value
                if len(meta.returns) > 2:
                    output_values[meta.returns[2].name] = total
                context.last_result = current_value
                return RuntimeEvent(
                    summary=meta.method_name,
                    payload=output_values or {"item": current_value},
                    next_flow_key="loop_body",
                    output_values=output_values,
                )
            state["index"] = 0
            context.last_result = total
            return RuntimeEvent(
                summary=meta.method_name,
                payload={"completed": total},
                next_flow_key="completed",
                output_values={"completed": total},
            )

        if control_kind == "blocking_delay_loop":
            seconds_value = max(0.0, as_float(kwargs.get("seconds"), 0.0))
            loops_value = max(0, as_int(kwargs.get("loops"), 1))
            total_delay = 0.0
            for _ in range(loops_value):
                time.sleep(seconds_value)
                total_delay += seconds_value
            context.last_result = total_delay
            return RuntimeEvent(
                summary=meta.method_name,
                payload={"total_delay": total_delay},
                next_flow_key="flow_out",
                output_values={"total_delay": total_delay},
            )

        if control_kind == "terminate_flow":
            message = as_text(kwargs.get("message"), "Flow terminated")
            context.return_value = message
            context.last_result = message
            context.terminated = True
            return RuntimeEvent(
                summary=meta.method_name,
                payload={"status": message},
                next_flow_key=None,
                output_values={"status": message},
            )

        raise RuntimeError(f"Unsupported control node kind: {control_kind}")

    def execute(self, context: Any) -> Any:
        meta = self._api_meta()
        kwargs = {param.name: self._resolve_param_value(context, param) for param in meta.params}
        if meta.is_control_node:
            event = self._execute_control_node(context, meta, kwargs)
            for key, value in event.output_values.items():
                context.set_port_value(self.id, key, value)
            return event

        module = importlib.import_module(meta.module_name)
        class_type = getattr(module, meta.class_name)
        context.api_instances.setdefault(meta.instance_key, class_type())
        instance = context.api_instances[meta.instance_key]
        result = getattr(instance, meta.method_name)(**kwargs)
        results = self._normalize_results(result)
        self._write_results_to_context(context, meta, results)
        payload: Any = results[0] if len(results) == 1 else results
        output_values = {
            ret.name: results[index] if index < len(results) else None
            for index, ret in enumerate(meta.returns)
        }
        return RuntimeEvent(summary=meta.method_name, payload=payload, next_flow_key="flow_out", output_values=output_values)

    def emit_python(self, export_context: Any) -> list[str]:
        meta = self._api_meta()
        lines: list[str] = []

        for param in meta.params:
            source = self.connected_data_source(param.name)
            source_code = repr((source[0].id, source[1])) if source is not None else "None"
            raw_value = self.get_property(param.name)
            if param.param_type == "bool":
                fallback_code = repr(as_bool(raw_value))
            elif param.param_type == "int":
                fallback_code = repr(as_int(raw_value))
            elif param.param_type == "float":
                fallback_code = repr(as_float(raw_value))
            else:
                fallback_code = repr(as_text(raw_value))
            raw_var = f"raw_{param.name}"
            lines.append(f"{raw_var} = _read_input_value(context, {source_code}, {fallback_code})")
            if param.param_type == "bool":
                lines.append(f"{param.name} = as_bool({raw_var})")
            elif param.param_type == "int":
                lines.append(f"{param.name} = as_int({raw_var})")
            elif param.param_type == "float":
                lines.append(f"{param.name} = as_float({raw_var})")
            elif param.param_type in {'handle', 'var_ref'}:
                lines.append(
                    f"{param.name} = context['variables'].get(as_text({raw_var}), as_text({raw_var}))"
                )
            else:
                lines.append(f"{param.name} = as_text({raw_var})")

        if meta.is_control_node:
            if meta.control_kind == "blocking_delay_loop":
                export_context.require_general_helper()
            return self._emit_control_python(meta, lines)

        export_context.require_api_import(meta.export_module_name, meta.class_name)
        instance_var = self._instance_var_name(export_context, meta)
        lines.extend(
            [
                f"{instance_var} = context.setdefault('api_instances', {{}}).get({meta.instance_key!r}) or {meta.class_name}()",
                f"context['api_instances'][{meta.instance_key!r}] = {instance_var}",
                f"result_list = {instance_var}.{meta.method_name}({', '.join(f'{param.name}={param.name}' for param in meta.params)})",
                "if result_list is None:",
                "    result_list = []",
                "elif not isinstance(result_list, (list, tuple)):",
                "    result_list = [result_list]",
                "else:",
                "    result_list = list(result_list)",
            ]
        )

        if meta.returns:
            prefix = as_text(self.get_property("save_prefix"), meta.method_name)
            for index, ret in enumerate(meta.returns):
                value_var = f"value_{ret.name}"
                lines.append(f"{value_var} = result_list[{index}] if len(result_list) > {index} else None")
                lines.append(f"_set_output_value(context, {self.id!r}, {ret.name!r}, {value_var})")
                lines.append(f"context['variables'][{ret.name!r}] = {value_var}")
                lines.append(f"context['variables'][{(prefix + '.' + ret.name)!r}] = {value_var}")
            if len(meta.returns) == 1:
                lines.append(f"context['last_result'] = context['variables'][{meta.returns[0].name!r}]")
            else:
                lines.append(
                    "context['last_result'] = ["
                    + ", ".join(f"context['variables'][{ret.name!r}]" for ret in meta.returns)
                    + "]"
                )
        else:
            lines.append("context['last_result'] = result_list[0] if len(result_list) == 1 else (result_list if result_list else None)")
        lines.append("return 'flow_out'")
        return lines

    def _emit_control_python(self, meta: ApiMethodMeta, lines: list[str]) -> list[str]:
        control_kind = meta.control_kind
        if control_kind in {"if_branch", "elif_branch"}:
            if control_kind == "elif_branch":
                lines.append("matched = (not as_bool(previous_matched)) and as_bool(condition)")
                lines.append("selected = value if matched else ''")
            else:
                lines.append("matched = as_bool(condition)")
                lines.append("selected = true_value if matched else false_value")
            lines.append(f"_set_output_value(context, {self.id!r}, 'selected', selected)")
            lines.append(f"_set_output_value(context, {self.id!r}, 'matched', matched)")
            lines.append("context['last_result'] = selected")
            lines.append("return 'true_branch' if matched else 'false_branch'")
            return lines

        if control_kind == "else_branch":
            lines.append("selected = '' if as_bool(previous_matched) else value")
            lines.append(f"_set_output_value(context, {self.id!r}, 'selected', selected)")
            lines.append("context['last_result'] = selected")
            lines.append("return 'skipped' if as_bool(previous_matched) else 'else_branch'")
            return lines

        if control_kind == "while_loop":
            lines.extend(
                [
                    f"state = context.setdefault('loop_states', {{}}).setdefault({self.id!r}, {{'count': 0}})",
                    "max_iterations = max(0, as_int(max_iterations))",
                    "if as_bool(condition) and state['count'] < max_iterations:",
                    "    state['count'] += 1",
                    "    _set_output_value(context, "
                    + repr(self.id)
                    + ", 'iterations', state['count'])",
                    "    context['last_result'] = state['count']",
                    "    return 'loop_body'",
                    "total_iterations = state.get('count', 0)",
                    "state['count'] = 0",
                    "context['last_result'] = total_iterations",
                    f"_set_output_value(context, {self.id!r}, 'iterations', total_iterations)",
                    "return 'completed'",
                ]
            )
            return lines

        if control_kind == "for_range":
            lines.extend(
                [
                    f"state = context.setdefault('loop_states', {{}}).setdefault({self.id!r}, {{'index': 0}})",
                    "total_iterations = max(0, as_int(value))",
                    "if state['index'] < total_iterations:",
                    "    current_value = state['index']",
                    "    state['index'] += 1",
                    f"    _set_output_value(context, {self.id!r}, 'current_value', current_value)",
                    f"    _set_output_value(context, {self.id!r}, 'current_index', current_value)",
                    "    context['last_result'] = current_value",
                    "    return 'loop_body'",
                    "state['index'] = 0",
                    "context['last_result'] = total_iterations",
                    "return 'completed'",
                ]
            )
            return lines

        if control_kind == "blocking_delay_loop":
            lines.extend(
                [
                    "total_delay = 0.0",
                    "for _ in range(max(0, as_int(loops))):",
                    "    general_helpers.delay(max(0.0, as_float(seconds)))",
                    "    total_delay += max(0.0, as_float(seconds))",
                    f"_set_output_value(context, {self.id!r}, 'total_delay', total_delay)",
                    "context['last_result'] = total_delay",
                    "return 'flow_out'",
                ]
            )
            return lines

        if control_kind == "terminate_flow":
            lines.extend(
                [
                    "context['return_value'] = as_text(message, 'Flow terminated')",
                    "context['last_result'] = context['return_value']",
                    "context['terminated'] = True",
                    "return None",
                ]
            )
            return lines

        return lines


def _parse_param(param_data: dict[str, Any]) -> MethodParamMeta:
    return MethodParamMeta(
        name=str(param_data.get("name", "")).strip(),
        zh=str(param_data.get("zh", param_data.get("name", ""))),
        param_type=str(param_data.get("type", "str")),
        required=bool(param_data.get("required", False)),
        default=param_data.get("default", ""),
        tooltip=str(param_data.get("tooltip", "")),
        options=tuple(param_data.get("options", []) or ()),
    )


def _parse_return(return_data: dict[str, Any]) -> MethodReturnMeta:
    return MethodReturnMeta(
        name=str(return_data.get("name", "value")),
        zh=str(return_data.get("zh", return_data.get("name", "value"))),
        return_type=str(return_data.get("type", "str")),
        tooltip=str(return_data.get("tooltip", "")),
    )


def _parse_flow_port(flow_data: dict[str, Any]) -> MethodFlowPortMeta:
    return MethodFlowPortMeta(
        key=str(flow_data.get("key", "")).strip(),
        zh=str(flow_data.get("zh", flow_data.get("key", ""))).strip(),
    )


def _default_control_payload(method_name: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "if_branch": {
            "control_kind": "if_branch",
            "flow_outputs": [
                {"key": "true_branch", "zh": "条件成立"},
                {"key": "false_branch", "zh": "条件不成立"},
            ],
        },
        "elif_branch": {
            "control_kind": "elif_branch",
            "flow_outputs": [
                {"key": "true_branch", "zh": "条件成立"},
                {"key": "false_branch", "zh": "条件不成立"},
            ],
        },
        "else_branch": {
            "control_kind": "else_branch",
            "flow_outputs": [
                {"key": "else_branch", "zh": "执行分支"},
                {"key": "skipped", "zh": "跳过"},
            ],
        },
        "while_loop": {
            "control_kind": "while_loop",
            "flow_outputs": [
                {"key": "loop_body", "zh": "循环体"},
                {"key": "completed", "zh": "完成"},
            ],
        },
        "for_range": {
            "control_kind": "for_range",
            "flow_outputs": [
                {"key": "loop_body", "zh": "循环体"},
                {"key": "completed", "zh": "完成"},
            ],
        },
        "blocking_delay_loop": {
            "control_kind": "blocking_delay_loop",
            "flow_outputs": [
                {"key": "flow_out", "zh": "继续"},
            ],
        },
        "terminate_flow": {
            "control_kind": "terminate_flow",
            "flow_outputs": [],
        },
    }
    return defaults.get(method_name, {})


def _parse_method_meta(module_name: str, class_name: str, method_name: str, doc_string: str) -> ApiMethodMeta | None:
    try:
        payload = json.loads(doc_string)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if "func_desc" not in payload:
        return None
    payload = {**_default_control_payload(method_name), **payload}

    params = tuple(_parse_param(item) for item in payload.get("params", []) if isinstance(item, dict) and item.get("name"))
    returns = tuple(_parse_return(item) for item in payload.get("returns", []) if isinstance(item, dict))
    flow_outputs = tuple(
        _parse_flow_port(item)
        for item in payload.get("flow_outputs", [])
        if isinstance(item, dict) and item.get("key")
    )
    return ApiMethodMeta(
        module_name=module_name,
        class_name=class_name,
        method_name=method_name,
        func_desc=str(payload.get("func_desc", "")),
        node_name_zh=str(payload.get("node_name_zh", payload.get("node_title_zh", method_name))),
        node_name_en=str(payload.get("node_name_en", payload.get("node_title_en", method_name))),
        category_zh=str(payload.get("category_zh", payload.get("category", class_name))),
        category_en=str(payload.get("category_en", payload.get("category", class_name))),
        icon_name=str(payload.get("icon", "")),
        control_kind=str(payload.get("control_kind", "")),
        flow_outputs=flow_outputs,
        params=params,
        returns=returns,
    )


LAST_API_DISCOVERY_FROM_CACHE = False
_METAS_MEMORY: list[ApiMethodMeta] | None = None
_METAS_MEMORY_FP: str | None = None


def _instrument_package_fingerprint(base_package: str = "demo_02.Instruments_pythonic") -> str:
    package = importlib.import_module(base_package)
    base_path = Path(next(iter(package.__path__)))
    digest = hashlib.sha256()
    for path in sorted(base_path.glob("*.py")):
        if path.name.startswith("_"):
            continue
        digest.update(path.name.encode())
        digest.update(str(path.stat().st_mtime_ns).encode("ascii"))
    return digest.hexdigest()


def _meta_from_json_dict(d: dict[str, Any]) -> ApiMethodMeta:
    params = tuple(
        MethodParamMeta(
            name=str(p["name"]),
            zh=str(p.get("zh", "")),
            param_type=str(p.get("param_type", "str")),
            required=bool(p.get("required", False)),
            default=p.get("default"),
            tooltip=str(p.get("tooltip", "")),
            options=tuple(p.get("options") or ()),
        )
        for p in d.get("params", [])
    )
    returns = tuple(
        MethodReturnMeta(
            name=str(r["name"]),
            zh=str(r.get("zh", "")),
            return_type=str(r.get("return_type", "str")),
            tooltip=str(r.get("tooltip", "")),
        )
        for r in d.get("returns", [])
    )
    flow_outputs = tuple(
        MethodFlowPortMeta(key=str(f["key"]), zh=str(f.get("zh", ""))) for f in d.get("flow_outputs", [])
    )
    return ApiMethodMeta(
        module_name=str(d["module_name"]),
        class_name=str(d["class_name"]),
        method_name=str(d["method_name"]),
        func_desc=str(d.get("func_desc", "")),
        node_name_zh=str(d.get("node_name_zh", "")),
        node_name_en=str(d.get("node_name_en", "")),
        category_zh=str(d.get("category_zh", "")),
        category_en=str(d.get("category_en", "")),
        icon_name=str(d.get("icon_name", "")),
        control_kind=str(d.get("control_kind", "")),
        flow_outputs=flow_outputs,
        params=params,
        returns=returns,
    )


def _discover_api_method_metas_scan(base_package: str = "demo_02.Instruments_pythonic") -> list[ApiMethodMeta]:
    package = importlib.import_module(base_package)
    metas: list[ApiMethodMeta] = []
    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.name.startswith("_"):
            continue
        full_module_name = f"{base_package}.{module_info.name}"
        module = importlib.import_module(full_module_name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != full_module_name:
                continue
            for method_name, method in inspect.getmembers(cls, inspect.isfunction):
                if method_name.startswith("_"):
                    continue
                doc_string = (method.__doc__ or "").strip()
                meta = _parse_method_meta(full_module_name, cls.__name__, method_name, doc_string)
                if meta:
                    metas.append(meta)
    return metas


def discover_api_method_metas(base_package: str = "demo_02.Instruments_pythonic") -> list[ApiMethodMeta]:
    """Scan ``Instruments_pythonic`` (or use JSON cache under ``generated/``). Sorted by category/class/method."""
    global LAST_API_DISCOVERY_FROM_CACHE, _METAS_MEMORY, _METAS_MEMORY_FP

    fp = _instrument_package_fingerprint(base_package)
    if _METAS_MEMORY is not None and _METAS_MEMORY_FP == fp:
        LAST_API_DISCOVERY_FROM_CACHE = True
        return list(_METAS_MEMORY)

    ensure_directory(GENERATED_DIR)
    cache_path = GENERATED_DIR / "api_discovery_cache.json"
    if cache_path.is_file():
        try:
            raw = json.loads(cache_path.read_text(encoding="utf-8"))
            if raw.get("fingerprint") == fp:
                metas = [_meta_from_json_dict(item) for item in raw.get("metas", [])]
                metas.sort(key=lambda m: (m.category_en.lower(), m.class_name.lower(), m.method_name))
                _METAS_MEMORY = metas
                _METAS_MEMORY_FP = fp
                LAST_API_DISCOVERY_FROM_CACHE = True
                return list(metas)
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            pass

    metas = _discover_api_method_metas_scan(base_package)
    metas.sort(key=lambda m: (m.category_en.lower(), m.class_name.lower(), m.method_name))
    try:
        cache_path.write_text(
            json.dumps({"fingerprint": fp, "metas": [asdict(m) for m in metas]}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass
    _METAS_MEMORY = metas
    _METAS_MEMORY_FP = fp
    LAST_API_DISCOVERY_FROM_CACHE = False
    return list(metas)


_DYNAMIC_CLASS_CACHE: dict[str, type[DynamicApiMethodNode]] = {}


def get_or_create_dynamic_class(meta: ApiMethodMeta) -> type[DynamicApiMethodNode]:
    key = meta.registry_key
    cached = _DYNAMIC_CLASS_CACHE.get(key)
    if cached is not None:
        return cached
    color = _rgb_for_category(meta.category_en)
    attrs = {
        "__identifier__": meta.node_identifier,
        "NODE_NAME": meta.node_name_zh,
        "DISPLAY_NAME_ZH": meta.node_name_zh,
        "DISPLAY_NAME_EN": meta.node_name_en,
        "CATEGORY_ZH": meta.category_zh,
        "CATEGORY_EN": meta.category_en,
        "DESCRIPTION_ZH": meta.func_desc,
        "DESCRIPTION_EN": meta.func_desc,
        "COLOR": color,
        "ICON_NAME": meta.icon_name,
        "API_META": meta,
        "FIELD_SPECS": _field_specs_from_meta(meta),
        "FLOW_INPUT_SPECS": _flow_input_specs_from_meta(meta),
        "DATA_INPUT_SPECS": _data_input_specs_from_meta(meta),
        "DATA_OUTPUT_SPECS": _data_output_specs_from_meta(meta),
        "FLOW_OUTPUT_SPECS": _flow_output_specs_from_meta(meta),
        "SESSION_BINDING": "none",
    }
    dynamic_class = type(meta.dynamic_class_name, (DynamicApiMethodNode,), attrs)
    _DYNAMIC_CLASS_CACHE[key] = dynamic_class
    return dynamic_class


def build_dynamic_node_classes(metas: list[ApiMethodMeta]) -> list[type[DynamicApiMethodNode]]:
    return [get_or_create_dynamic_class(meta) for meta in metas]

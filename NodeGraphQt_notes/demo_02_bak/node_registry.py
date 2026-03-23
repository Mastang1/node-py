from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

from NodeGraphQt.constants import PortTypeEnum

from .common import LANG_ZH
from .common import data_type_compatible
from .nodes import ALL_NODE_CLASSES, WorkflowNode

_STATIC_NODE_CLASSES: tuple[type[WorkflowNode], ...] = tuple(ALL_NODE_CLASSES)
_GRAPH_REGISTERED_TYPES: set[str] = set()
_API_NODE_CLASSES: dict[str, type[WorkflowNode]] = {}


@dataclass(frozen=True)
class ResourceTemplate:
    node_class: type[WorkflowNode]

    def category(self, language: str = LANG_ZH) -> str:
        return self.node_class.category_name(language)

    def label(self, language: str = LANG_ZH) -> str:
        return self.node_class.display_name(language)

    def tooltip(self, language: str = LANG_ZH) -> str:
        return self.node_class.description(language)

    def node_type(self) -> str:
        return self.node_class.type_

    def icon_path(self) -> str:
        return self.node_class.icon_path()


def iter_all_node_classes() -> list[type[WorkflowNode]]:
    return list(_STATIC_NODE_CLASSES) + list(_API_NODE_CLASSES.values())


def all_templates() -> list[ResourceTemplate]:
    return [ResourceTemplate(node_class=node_class) for node_class in iter_all_node_classes()]


def grouped_templates(language: str = LANG_ZH) -> OrderedDict[str, list[ResourceTemplate]]:
    grouped: OrderedDict[str, list[ResourceTemplate]] = OrderedDict()
    for template in all_templates():
        category = template.category(language)
        grouped.setdefault(category, []).append(template)
    return grouped


def register_all_nodes(graph: object) -> None:
    graph.register_nodes(list(_STATIC_NODE_CLASSES))
    for cls in _STATIC_NODE_CLASSES:
        _GRAPH_REGISTERED_TYPES.add(cls.type_)
    configure_graph_port_constraints(graph)


def ensure_instrument_api_registered(graph: object) -> tuple[int, int]:
    """Discover JSON-documented API methods, register node types on the graph, refresh template index.

    Returns ``(newly_registered_count, total_api_count)``.
    """
    from .api_dynamic_nodes import discover_api_method_metas, get_or_create_dynamic_class

    metas = discover_api_method_metas()
    new_types: list[type[WorkflowNode]] = []
    for meta in metas:
        cls = get_or_create_dynamic_class(meta)
        _API_NODE_CLASSES[cls.type_] = cls
        if cls.type_ not in _GRAPH_REGISTERED_TYPES:
            new_types.append(cls)
            _GRAPH_REGISTERED_TYPES.add(cls.type_)
    if new_types:
        graph.register_nodes(new_types)
    configure_graph_port_constraints(graph)
    return len(new_types), len(metas)


def api_node_template_count() -> int:
    return len(_API_NODE_CLASSES)


def configure_graph_port_constraints(graph: object) -> None:
    graph.model.accept_connection_types = {}
    graph.model.reject_connection_types = {}
    graph.viewer().accept_connection_types = graph.model.accept_connection_types
    graph.viewer().reject_connection_types = graph.model.reject_connection_types
    node_classes = iter_all_node_classes()

    for target_cls in node_classes:
        for input_spec in target_cls.flow_input_specs():
            for source_cls in node_classes:
                for output_spec in source_cls.flow_output_specs():
                    graph.model.add_port_accept_connection_type(
                        port_name=input_spec.label,
                        port_type=PortTypeEnum.IN.value,
                        node_type=target_cls.type_,
                        accept_pname=output_spec.label,
                        accept_ptype=PortTypeEnum.OUT.value,
                        accept_ntype=source_cls.type_,
                    )

        for input_spec in target_cls.data_input_specs():
            for source_cls in node_classes:
                for output_spec in source_cls.data_output_specs():
                    if not data_type_compatible(output_spec.data_type, input_spec.data_type):
                        continue
                    graph.model.add_port_accept_connection_type(
                        port_name=input_spec.label,
                        port_type=PortTypeEnum.IN.value,
                        node_type=target_cls.type_,
                        accept_pname=output_spec.label,
                        accept_ptype=PortTypeEnum.OUT.value,
                        accept_ntype=source_cls.type_,
                    )

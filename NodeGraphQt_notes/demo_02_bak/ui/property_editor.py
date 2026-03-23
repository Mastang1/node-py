from __future__ import annotations

from Qt import QtCore, QtWidgets

from ..common import LANG_ZH
from ..nodes import WorkflowNode


class NodePropertyEditor(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._language = LANG_ZH
        self._node: WorkflowNode | None = None
        self._updating = False
        self._widgets: dict[str, QtWidgets.QWidget] = {}

        self._title = QtWidgets.QLabel()
        self._type = QtWidgets.QLabel()
        self._empty = QtWidgets.QLabel()
        self._empty.setAlignment(QtCore.Qt.AlignCenter)

        self._form_widget = QtWidgets.QWidget()
        self._form_layout = QtWidgets.QFormLayout(self._form_widget)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self._form_layout.setSpacing(8)

        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self._form_widget)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._title)
        layout.addWidget(self._type)
        layout.addWidget(self._empty)
        layout.addWidget(self._scroll, 1)

        self.set_node(None)

    def retranslate(self, language: str) -> None:
        self._language = language
        self.set_node(self._node)

    def set_node(self, node: WorkflowNode | None) -> None:
        self._node = node
        self._clear_form()
        self._widgets.clear()

        if node is None:
            self._title.setText("未选中节点" if self._language == LANG_ZH else "No node selected")
            self._type.setText("")
            self._empty.setText("请选择画布中的节点。" if self._language == LANG_ZH else "Select a node on the canvas.")
            self._empty.show()
            self._scroll.hide()
            return

        self._title.setText(node.name())
        self._type.setText(f"{node.__class__.__name__} | {node.category_name(self._language)}")
        self._empty.hide()
        self._scroll.show()

        name_edit = QtWidgets.QLineEdit(node.name())
        name_edit.setToolTip("节点显示名" if self._language == LANG_ZH else "Node display name")
        name_edit.editingFinished.connect(lambda: node.set_name(name_edit.text()))
        self._widgets["name"] = name_edit
        self._form_layout.addRow("名称" if self._language == LANG_ZH else "Name", name_edit)

        for field in node.field_specs():
            label = field.label(self._language)
            tooltip = field.tooltip(self._language)
            widget = self._create_widget(node, field.name)
            widget.setToolTip(tooltip)
            self._widgets[field.name] = widget
            self._form_layout.addRow(label, widget)

    def update_current_node_property(self, prop_name: str, prop_value: object) -> None:
        if not self._node or prop_name not in self._widgets:
            return
        widget = self._widgets[prop_name]
        self._updating = True
        try:
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.setText("" if prop_value is None else str(prop_value))
            elif isinstance(widget, QtWidgets.QPlainTextEdit):
                widget.setPlainText("" if prop_value is None else str(prop_value))
            elif isinstance(widget, QtWidgets.QComboBox):
                index = widget.findText("" if prop_value is None else str(prop_value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(bool(prop_value))
        finally:
            self._updating = False

    def _clear_form(self) -> None:
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            label = item.widget()
            if label:
                label.deleteLater()
            child_layout = item.layout()
            if child_layout:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget:
                        child_widget.deleteLater()

    def _create_widget(self, node: WorkflowNode, field_name: str) -> QtWidgets.QWidget:
        field = node.field_spec(field_name)
        value = node.get_property(field_name)

        if field.kind == "bool":
            widget = QtWidgets.QCheckBox()
            widget.setChecked(bool(value))
            widget.toggled.connect(lambda checked, name=field_name: self._apply_value(name, checked))
            return widget

        if field.kind == "enum":
            widget = QtWidgets.QComboBox()
            widget.addItems(list(field.options))
            current_index = widget.findText("" if value is None else str(value))
            if current_index >= 0:
                widget.setCurrentIndex(current_index)
            widget.currentTextChanged.connect(lambda text, name=field_name: self._apply_value(name, text))
            return widget

        if field.kind == "multiline" or field.multiline:
            widget = QtWidgets.QPlainTextEdit()
            widget.setPlainText("" if value is None else str(value))
            widget.textChanged.connect(lambda name=field_name, editor=widget: self._apply_value(name, editor.toPlainText()))
            return widget

        widget = QtWidgets.QLineEdit("" if value is None else str(value))
        widget.setPlaceholderText(field.placeholder(self._language))
        widget.editingFinished.connect(lambda name=field_name, editor=widget: self._apply_value(name, editor.text()))
        return widget

    def _apply_value(self, name: str, value: object) -> None:
        if self._updating or not self._node:
            return
        self._node.set_property(name, value)

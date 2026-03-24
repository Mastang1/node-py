from __future__ import annotations

from Qt import QtCore, QtGui, QtWidgets
from NodeGraphQt.constants import MIME_TYPE, URN_SCHEME

from ..common import LANG_ZH
from ..node_registry import grouped_templates


class _TemplateTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def mimeData(self, items: list[QtWidgets.QTreeWidgetItem]) -> QtCore.QMimeData:  # type: ignore[override]
        node_types: list[str] = []
        for item in items:
            node_type = item.data(0, QtCore.Qt.UserRole)
            if node_type:
                node_types.append(str(node_type))
        mime_data = QtCore.QMimeData()
        if node_types:
            node_urn = URN_SCHEME + ";".join(f"node:{node_type}" for node_type in node_types)
            mime_data.setData(MIME_TYPE, QtCore.QByteArray(node_urn.encode()))
        return mime_data


class ResourceTreeWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._language = LANG_ZH
        self._view_mode = "grouped"

        self._search = QtWidgets.QLineEdit()
        self._search.textChanged.connect(self._apply_filter)

        self._view_mode_combo = QtWidgets.QComboBox()
        self._view_mode_combo.currentIndexChanged.connect(self._on_view_mode_changed)

        self._tree = _TemplateTreeWidget()
        self._tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_tree_context_menu)

        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(6)
        controls_layout.addWidget(self._search, 1)
        controls_layout.addWidget(self._view_mode_combo)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(controls)
        layout.addWidget(self._tree, 1)

        self.retranslate(self._language)

    def retranslate(self, language: str) -> None:
        self._language = language
        self._search.setPlaceholderText("搜索节点..." if language == LANG_ZH else "Search nodes...")
        self._view_mode_combo.blockSignals(True)
        current_mode = self._view_mode
        self._view_mode_combo.clear()
        self._view_mode_combo.addItem("按分类" if language == LANG_ZH else "By Category", "grouped")
        self._view_mode_combo.addItem("全部节点" if language == LANG_ZH else "All Nodes", "flat")
        self._view_mode_combo.setToolTip("节点列表展示方式" if language == LANG_ZH else "Node list display mode")
        index = self._view_mode_combo.findData(current_mode)
        if index < 0:
            index = 0
        self._view_mode_combo.setCurrentIndex(index)
        self._view_mode_combo.blockSignals(False)
        self.rebuild()

    def rebuild(self) -> None:
        self._tree.clear()
        groups = grouped_templates(self._language)
        if self._view_mode == "flat":
            category_title = "全部节点" if self._language == LANG_ZH else "All Nodes"
            category_item = QtWidgets.QTreeWidgetItem([category_title])
            category_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self._tree.addTopLevelItem(category_item)
            category_item.setExpanded(True)
            all_templates = [
                template
                for templates in groups.values()
                for template in templates
            ]
            for template in sorted(all_templates, key=lambda item: item.label(self._language).lower()):
                child = QtWidgets.QTreeWidgetItem([template.label(self._language)])
                child.setIcon(0, QtGui.QIcon(template.icon_path()))
                child.setToolTip(0, template.tooltip(self._language))
                child.setData(0, QtCore.Qt.UserRole, template.node_type())
                child.setData(0, QtCore.Qt.UserRole + 1, template.label(self._language).lower())
                category_item.addChild(child)
            self._apply_filter(self._search.text())
            return

        for category in sorted(groups.keys(), key=str.lower):
            templates = sorted(groups[category], key=lambda item: item.label(self._language).lower())
            category_item = QtWidgets.QTreeWidgetItem([category])
            category_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self._tree.addTopLevelItem(category_item)
            category_item.setExpanded(True)
            for template in templates:
                child = QtWidgets.QTreeWidgetItem([template.label(self._language)])
                child.setIcon(0, QtGui.QIcon(template.icon_path()))
                child.setToolTip(0, template.tooltip(self._language))
                child.setData(0, QtCore.Qt.UserRole, template.node_type())
                child.setData(0, QtCore.Qt.UserRole + 1, template.label(self._language).lower())
                category_item.addChild(child)
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str) -> None:
        keyword = text.strip().lower()
        for i in range(self._tree.topLevelItemCount()):
            category_item = self._tree.topLevelItem(i)
            visible_children = 0
            for j in range(category_item.childCount()):
                child = category_item.child(j)
                if not keyword:
                    child.setHidden(False)
                    visible_children += 1
                    continue
                haystack = child.data(0, QtCore.Qt.UserRole + 1) or ""
                matched = keyword in str(haystack)
                child.setHidden(not matched)
                if matched:
                    visible_children += 1
            category_item.setHidden(visible_children == 0)

    def _on_view_mode_changed(self, _index: int) -> None:
        self._view_mode = str(self._view_mode_combo.currentData() or "grouped")
        self.rebuild()

    def _on_tree_context_menu(self, position: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        expand_text = "展开全部" if self._language == LANG_ZH else "Expand All"
        collapse_text = "收缩全部" if self._language == LANG_ZH else "Collapse All"
        menu.addAction(expand_text, self._tree.expandAll)
        menu.addAction(collapse_text, self._tree.collapseAll)
        menu.exec_(self._tree.viewport().mapToGlobal(position))

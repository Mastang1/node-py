from __future__ import annotations

from typing import Any, Callable

from Qt import QtCore, QtWidgets


class ConnectionManagerDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.resize(860, 620)
        self._entries: list[dict[str, str]] = []
        self._locate_source_callback: Callable[[dict[str, Any]], None] | None = None
        self._locate_target_callback: Callable[[dict[str, Any]], None] | None = None
        self._highlight_callback: Callable[[dict[str, Any]], None] | None = None

        self._filter_combo = QtWidgets.QComboBox()
        self._filter_combo.currentIndexChanged.connect(self._render)

        self._tree = QtWidgets.QTreeWidget()
        self._tree.setRootIsDecorated(False)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._tree.setUniformRowHeights(True)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._tree.setColumnCount(6)
        self._tree.setHeaderLabels(["Type", "Source", "Out", "Target", "In", "Notes"])

        self._btn_locate_source = QtWidgets.QPushButton("Locate Source")
        self._btn_locate_source.clicked.connect(self._on_locate_source)
        self._btn_locate_target = QtWidgets.QPushButton("Locate Target")
        self._btn_locate_target.clicked.connect(self._on_locate_target)
        self._btn_highlight = QtWidgets.QPushButton("Highlight Connection")
        self._btn_highlight.clicked.connect(self._on_highlight)

        self._btn_close = QtWidgets.QPushButton("Close")
        self._btn_close.clicked.connect(self.accept)

        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self._filter_combo)
        controls_layout.addStretch(1)

        buttons = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addWidget(self._btn_locate_source)
        buttons_layout.addWidget(self._btn_locate_target)
        buttons_layout.addWidget(self._btn_highlight)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self._btn_close)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(controls)
        layout.addWidget(self._tree, 1)
        layout.addWidget(buttons)

    def set_title(self, title: str) -> None:
        self.setWindowTitle(title)

    def set_close_text(self, text: str) -> None:
        self._btn_close.setText(text)

    def set_action_texts(self, locate_source: str, locate_target: str, highlight: str) -> None:
        self._btn_locate_source.setText(locate_source)
        self._btn_locate_target.setText(locate_target)
        self._btn_highlight.setText(highlight)

    def set_callbacks(
        self,
        *,
        locate_source: Callable[[dict[str, Any]], None] | None = None,
        locate_target: Callable[[dict[str, Any]], None] | None = None,
        highlight: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._locate_source_callback = locate_source
        self._locate_target_callback = locate_target
        self._highlight_callback = highlight

    def set_filters(self, filters: list[tuple[str, str]]) -> None:
        current = self._filter_combo.currentData()
        self._filter_combo.blockSignals(True)
        self._filter_combo.clear()
        for label, value in filters:
            self._filter_combo.addItem(label, value)
        index = self._filter_combo.findData(current)
        if index < 0:
            index = 0
        self._filter_combo.setCurrentIndex(index)
        self._filter_combo.blockSignals(False)

    def set_entries(self, entries: list[dict[str, str]]) -> None:
        self._entries = entries
        self._render()

    def _render(self) -> None:
        filter_value = str(self._filter_combo.currentData() or "all")
        visible_entries = [
            entry for entry in self._entries
            if filter_value == "all" or entry.get("kind") == filter_value
        ]
        self._tree.clear()
        if not visible_entries:
            self._tree.setHeaderHidden(True)
            item = QtWidgets.QTreeWidgetItem(["No connections."])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self._tree.addTopLevelItem(item)
            return
        self._tree.setHeaderHidden(False)
        for entry in visible_entries:
            item = QtWidgets.QTreeWidgetItem(
                [
                    str(entry.get("kind", "")),
                    str(entry.get("source_name", "")),
                    str(entry.get("source_port", "")),
                    str(entry.get("target_name", "")),
                    str(entry.get("target_port", "")),
                    str(entry.get("message", "")),
                ]
            )
            item.setData(0, QtCore.Qt.UserRole, entry)
            self._tree.addTopLevelItem(item)
        self._tree.resizeColumnToContents(0)
        self._tree.resizeColumnToContents(1)
        self._tree.resizeColumnToContents(2)
        self._tree.resizeColumnToContents(3)
        self._tree.resizeColumnToContents(4)

    def _current_entry(self) -> dict[str, Any] | None:
        item = self._tree.currentItem()
        if item is None:
            return None
        entry = item.data(0, QtCore.Qt.UserRole)
        return entry if isinstance(entry, dict) else None

    def _on_locate_source(self) -> None:
        entry = self._current_entry()
        if entry and self._locate_source_callback:
            self._locate_source_callback(entry)

    def _on_locate_target(self) -> None:
        entry = self._current_entry()
        if entry and self._locate_target_callback:
            self._locate_target_callback(entry)

    def _on_highlight(self) -> None:
        entry = self._current_entry()
        if entry and self._highlight_callback:
            self._highlight_callback(entry)

    def _on_item_double_clicked(self, item: QtWidgets.QTreeWidgetItem, _column: int) -> None:
        entry = item.data(0, QtCore.Qt.UserRole)
        if isinstance(entry, dict) and self._highlight_callback:
            self._highlight_callback(entry)

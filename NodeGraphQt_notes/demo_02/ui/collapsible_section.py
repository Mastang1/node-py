from __future__ import annotations

from Qt import QtCore, QtWidgets


class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title: str = "", parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._toggle = QtWidgets.QToolButton(text=title)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(True)
        self._toggle.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self._toggle.setArrowType(QtCore.Qt.DownArrow)
        self._toggle.clicked.connect(self._on_toggle)

        self._content = QtWidgets.QFrame()
        self._content.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self._content_layout = QtWidgets.QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(6, 6, 6, 6)
        self._content_layout.setSpacing(6)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._toggle)
        layout.addWidget(self._content)

    def _on_toggle(self, checked: bool) -> None:
        self._toggle.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)
        self._content.setVisible(checked)

    def set_title(self, title: str) -> None:
        self._toggle.setText(title)

    def set_tooltip(self, text: str) -> None:
        self._toggle.setToolTip(text)
        self._content.setToolTip(text)

    def add_widget(self, widget: QtWidgets.QWidget) -> None:
        self._content_layout.addWidget(widget)

    def clear(self) -> None:
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def content_layout(self) -> QtWidgets.QVBoxLayout:
        return self._content_layout

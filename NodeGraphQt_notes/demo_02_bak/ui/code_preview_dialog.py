from __future__ import annotations

from Qt import QtGui, QtWidgets


class CodePreviewDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.resize(900, 680)

        self._editor = QtWidgets.QTextEdit()
        self._editor.setReadOnly(True)
        font = QtGui.QFont("Consolas")
        if not font.exactMatch():
            font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.Monospace)
        self._editor.setFont(font)

        self._btn_close = QtWidgets.QPushButton("Close")
        self._btn_close.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._editor, 1)
        layout.addWidget(self._btn_close)

    def set_title(self, title: str) -> None:
        self.setWindowTitle(title)

    def set_close_text(self, text: str) -> None:
        self._btn_close.setText(text)

    def set_code(self, code: str) -> None:
        try:
            from pygments import highlight
            from pygments.formatters import HtmlFormatter
            from pygments.lexers import PythonLexer
        except ImportError:
            self._editor.setPlainText(code)
            return

        formatter = HtmlFormatter(style="monokai", noclasses=True, nowrap=False)
        body = highlight(code, PythonLexer(), formatter)
        css = formatter.get_style_defs(".highlight")
        wrapped = (
            "<html><head><meta charset=\"utf-8\">"
            f"<style>pre {{ margin: 0; }} {css}</style></head>"
            f"<body style=\"background:#272822;color:#f8f8f2;\"><div class=\"highlight\">{body}</div></body></html>"
        )
        self._editor.setHtml(wrapped)

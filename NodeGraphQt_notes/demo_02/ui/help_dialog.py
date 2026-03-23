"""Modal help browser for product-level user documentation."""

from __future__ import annotations

from Qt import QtCore, QtWidgets


def show_help_browser(parent: QtWidgets.QWidget, title: str, html: str) -> None:
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setWindowModality(QtCore.Qt.ApplicationModal)
    dialog.resize(620, 480)

    layout = QtWidgets.QVBoxLayout(dialog)
    browser = QtWidgets.QTextBrowser()
    browser.setOpenExternalLinks(True)
    browser.setHtml(html)
    layout.addWidget(browser)

    buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)

    dialog.exec()

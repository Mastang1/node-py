"""Platform adapters: persistent UI state without business rules."""
from __future__ import annotations

from typing import Any

from Qt import QtCore, QtWidgets


def _as_qbytearray(state: Any) -> QtCore.QByteArray | None:
    if state is None:
        return None
    if isinstance(state, QtCore.QByteArray):
        return state if not state.isEmpty() else None
    if isinstance(state, (bytes, bytearray, memoryview)):
        return QtCore.QByteArray(bytes(state))
    return None


class MainLayoutSettingsStore:
    """
    Saves/restores main splitter geometry and tab indices (IniFormat, user scope).
    Keys are internal; org/app names are stable for end-user QSettings migration.
    """

    ORGANIZATION = "Mastang"
    APPLICATION = "Demo02NodeFlow"

    def _settings(self) -> QtCore.QSettings:
        return QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            self.ORGANIZATION,
            self.APPLICATION,
        )

    def restore(
        self,
        h_splitter: QtWidgets.QSplitter | None,
        v_splitter: QtWidgets.QSplitter | None,
        right_tabs: QtWidgets.QTabWidget,
        log_tabs: QtWidgets.QTabWidget,
    ) -> None:
        if h_splitter is None or v_splitter is None:
            return
        s = self._settings()
        h_state = _as_qbytearray(s.value("layout/h_split"))
        if h_state is not None:
            h_splitter.restoreState(h_state)
        v_state = _as_qbytearray(s.value("layout/v_split"))
        if v_state is not None:
            v_splitter.restoreState(v_state)
        try:
            right_tabs.setCurrentIndex(int(s.value("layout/right_tab", 0)))
        except (TypeError, ValueError):
            pass
        try:
            log_tabs.setCurrentIndex(int(s.value("layout/log_tab", 0)))
        except (TypeError, ValueError):
            pass

    def save(
        self,
        h_splitter: QtWidgets.QSplitter | None,
        v_splitter: QtWidgets.QSplitter | None,
        right_tabs: QtWidgets.QTabWidget,
        log_tabs: QtWidgets.QTabWidget,
    ) -> None:
        if h_splitter is None or v_splitter is None:
            return
        s = self._settings()
        s.setValue("layout/h_split", h_splitter.saveState())
        s.setValue("layout/v_split", v_splitter.saveState())
        s.setValue("layout/right_tab", right_tabs.currentIndex())
        s.setValue("layout/log_tab", log_tabs.currentIndex())
        s.sync()

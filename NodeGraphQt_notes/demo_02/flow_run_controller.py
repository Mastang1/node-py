from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from Qt import QtCore

from .common import LANG_ZH


class FlowRunController(QtCore.QObject):
    """Runs ``headless_flow_runner`` in a QProcess so the main UI thread stays responsive."""

    logEmitted = QtCore.Signal(str, str)
    finishedRun = QtCore.Signal(bool, str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._proc = QtCore.QProcess(self)
        self._buffer = ""
        self._proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._on_ready_read)
        self._proc.finished.connect(self._on_finished)

    def is_running(self) -> bool:
        return self._proc.state() != QtCore.QProcess.NotRunning

    def start_run(self, json_path: Path, language: str = LANG_ZH) -> None:
        self._buffer = ""
        notes_dir = Path(__file__).resolve().parent.parent
        self._proc.setWorkingDirectory(str(notes_dir))
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("QT_QPA_PLATFORM", "offscreen")
        self._proc.setProcessEnvironment(env)
        self._proc.start(
            sys.executable,
            ["-m", "demo_02.headless_flow_runner", "run", str(json_path), "--lang", language],
        )

    def stop(self) -> None:
        if self.is_running():
            self._proc.kill()
            self._proc.waitForFinished(3000)

    def _on_ready_read(self) -> None:
        data = bytes(self._proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._buffer += data
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                payload: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                self.logEmitted.emit("run", line)
                continue
            if payload.get("type") == "log":
                self.logEmitted.emit(str(payload.get("channel", "run")), str(payload.get("message", "")))
            elif payload.get("type") == "result":
                pass

    def _on_finished(self, exit_code: int, exit_status: Any = None) -> None:
        if self._buffer.strip():
            self._on_ready_read()
        normal = getattr(QtCore.QProcess, "NormalExit", 0)
        st = exit_status if exit_status is not None else normal
        ok = exit_code == 0 and int(st) == int(normal)
        msg = "子进程运行结束" if ok else f"子进程异常退出 (code={exit_code})"
        self.finishedRun.emit(ok, msg)

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HEADLESS_SMOKE_FLAG = "--headless-smoke-test"
if HEADLESS_SMOKE_FLAG in sys.argv:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

THIS_FILE = Path(__file__).resolve()
PACKAGE_PARENT = THIS_FILE.parent.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from Qt import QtCore, QtWidgets

from demo_02.app_window import Demo02Window
from demo_02.assets_bootstrap import ensure_assets
from demo_02.common import DEFAULT_EXPORT_PATH, DEFAULT_FLOW_PATH
from demo_02.node_registry import ensure_instrument_api_registered
from demo_02.nodes import BooleanConstantNode, IntegerConstantNode
from demo_02.workflow_runtime import WorkflowRuntime
from demo_02.workflow_exporter import DEFAULT_RUN_FLOW_NAME


def _run_exported_linear_script_smoke(exported_path: Path) -> None:
    """Exec linear export module (imports + run_flow) and invoke run_flow() once."""
    text = exported_path.read_text(encoding="utf-8")
    if str(PACKAGE_PARENT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_PARENT))
    ns: dict[str, Any] = {"__builtins__": __builtins__}
    exec(compile(text, str(exported_path), "exec"), ns, ns)
    fn = ns.get(DEFAULT_RUN_FLOW_NAME)
    if fn is None or not callable(fn):
        raise RuntimeError(f"Export smoke: missing callable {DEFAULT_RUN_FLOW_NAME}()")
    fn()


def create_qapplication() -> QtWidgets.QApplication:
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    return app


def run_qt_app(app: QtWidgets.QApplication) -> int:
    if hasattr(app, "exec"):
        return app.exec()
    return app.exec_()


def run_headless_smoke_test() -> int:
    class _FakeSceneEvent:
        def __init__(self, scene_pos: QtCore.QPointF) -> None:
            self._scene_pos = scene_pos

        def scenePos(self) -> QtCore.QPointF:
            return self._scene_pos

    def _port_scene_pos(port: object) -> QtCore.QPointF:
        view = getattr(port, "view")
        return view.sceneBoundingRect().center()

    def _run_drag_validation(window: Demo02Window, app: QtWidgets.QApplication) -> None:
        window.new_flow(prompt_if_dirty=False)
        ensure_instrument_api_registered(window.graph)
        app.processEvents()

        bool_node = window.graph.create_node(BooleanConstantNode.type_, name="bool")
        int_node = window.graph.create_node(IntegerConstantNode.type_, name="int")
        loop_node = window.graph.create_node(
            window._dynamic_node_type("general", "GeneralFlowApi", "for_range"),
            name="for",
        )
        bool_node.set_pos(-180.0, -40.0)
        int_node.set_pos(-180.0, 120.0)
        loop_node.set_pos(140.0, 40.0)
        window._refresh_node_visuals()
        app.processEvents()

        viewer = window.graph.viewer()

        invalid_target = loop_node.data_input_port("value")
        bool_output = bool_node.data_output_port("value")
        viewer._origin_pos = viewer.mapFromScene(_port_scene_pos(bool_output))
        viewer._previous_pos = viewer._origin_pos
        viewer.start_live_connection(bool_output.view)
        invalid_event = _FakeSceneEvent(_port_scene_pos(invalid_target))
        viewer.sceneMouseMoveEvent(invalid_event)
        if "类型不兼容" not in window.statusBar().currentMessage():
            raise RuntimeError("GUI drag validation failed: missing invalid hover feedback during drag.")
        viewer.apply_live_connection(invalid_event)
        app.processEvents()

        invalid_connected = any(port.node().id == loop_node.id for port in bool_output.connected_ports())
        if invalid_connected:
            raise RuntimeError("GUI drag validation failed: invalid bool->int connection was not rejected.")
        if "类型不兼容" not in window.statusBar().currentMessage():
            raise RuntimeError("GUI drag validation failed: status bar feedback was not shown for invalid drag.")

        int_output = int_node.data_output_port("value")
        viewer._origin_pos = viewer.mapFromScene(_port_scene_pos(int_output))
        viewer._previous_pos = viewer._origin_pos
        viewer.start_live_connection(int_output.view)
        valid_event = _FakeSceneEvent(_port_scene_pos(invalid_target))
        viewer.sceneMouseMoveEvent(valid_event)
        viewer.apply_live_connection(valid_event)
        app.processEvents()

        valid_connected = any(port.node().id == loop_node.id for port in int_output.connected_ports())
        if not valid_connected:
            raise RuntimeError("GUI drag validation failed: valid int->int connection was not created.")

        window.log("all", "GUI 拖拽连线验证通过：错误色、提示文案与非法落线回滚均正常。")

    def _verify_connection_manager(window: Demo02Window) -> None:
        entries = window._collect_connection_entries()
        if not entries:
            raise RuntimeError("Connection manager verification failed: no connection entries collected.")
        window.connection_manager_dialog.set_entries(entries)
        window._highlight_connection_entry(entries[0])

    def _run_cycle(window: Demo02Window, export_path: Path) -> None:
        if not window.validate_flow():
            raise RuntimeError("Smoke test failed: validation did not pass.")

        flow_path = window._save_flow_to(DEFAULT_FLOW_PATH)
        window.node_runtime_states.clear()
        window._reset_runtime_visuals()
        runtime = WorkflowRuntime(
            window.graph,
            window.log,
            language=window.current_language,
            node_state_callback=window.on_runtime_node_state,
        )
        result = runtime.execute()
        if result is None:
            raise RuntimeError("Smoke test failed: runtime returned None.")

        exported_path = window.export_python(export_path)
        if exported_path is None:
            raise RuntimeError("Smoke test failed: export path is None.")

        window.load_flow_from_path(flow_path)
        if not window.validate_flow():
            raise RuntimeError("Smoke test failed: validation after reload did not pass.")

        try:
            _run_exported_linear_script_smoke(exported_path)
        except Exception as exc:
            raise RuntimeError(f"Smoke test failed: exported flow body did not execute: {exc}") from exc

    def _verify_headless_subprocess_runner(flow_json: Path) -> None:
        notes_dir = Path(__file__).resolve().parent.parent
        proc = subprocess.run(
            [sys.executable, "-m", "demo_02.headless_flow_runner", "run", str(flow_json), "--lang", "zh"],
            cwd=str(notes_dir),
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            raise RuntimeError(f"headless_flow_runner failed rc={proc.returncode}:\n{out}")
        if '"type": "result"' not in out or '"ok": true' not in out:
            raise RuntimeError(f"headless_flow_runner missing ok result JSON in:\n{out}")

    def _verify_debug_session(window: Demo02Window, app: QtWidgets.QApplication) -> None:
        window.new_flow(prompt_if_dirty=False)
        window.build_sample_flow(prompt_if_dirty=False)
        app.processEvents()
        if not window.validate_flow():
            raise RuntimeError("Debug smoke: validation failed.")
        window.debug_session.clear_breakpoints()
        window.node_runtime_states.clear()
        window._reset_runtime_visuals()
        window._apply_breakpoint_overlays()
        window.debug_session.reset_for_new_run()
        failed: list[str] = []

        def on_failed(msg: str) -> None:
            failed.append(msg)
            window.log("run", f"[调试] smoke 失败: {msg}")

        def kick_continue() -> None:
            window.debug_continue_run()

        dw = window.create_flow_debug_worker()
        window._debug_worker = dw
        window._update_execution_action_states()
        dw.run_failed.connect(on_failed)
        window.log("run", "[调试] smoke：子线程 execute_debug + 主线程 continue（processEvents 轮询）。")
        dw.start()
        # Unblock first wait_before_node immediately: zero-timer may be starved or run after a long wait.
        window.debug_continue_run()
        QtCore.QTimer.singleShot(0, kick_continue)
        deadline = time.time() + 120.0
        while window._debug_worker is not None and time.time() < deadline:
            app.processEvents(QtCore.QEventLoop.AllEvents, 50)
            # Thread finished but queued run_finished not yet delivered — keep pumping.
            if window._debug_worker is not None:
                try:
                    worker_still_running = dw.isRunning()
                except RuntimeError:
                    worker_still_running = False
                if not worker_still_running:
                    app.processEvents(QtCore.QEventLoop.AllEvents, 100)
        app.processEvents()
        if failed:
            raise RuntimeError(f"Debug smoke: worker failed: {failed[0]}")
        if window._debug_worker is not None:
            window.stop_debug_flow()
            app.processEvents()
            raise RuntimeError("Debug smoke: worker still registered (timeout).")

    # Avoid flooding stdout (IDE / pipe buffers): keeps Qt processEvents responsive during smoke.
    os.environ["DEMO02_QUIET_SMOKE"] = "1"

    ensure_assets()
    app = create_qapplication()
    window = Demo02Window()
    window.show()
    app.processEvents()

    _run_drag_validation(window, app)

    window.build_dynamic_sample_flow(prompt_if_dirty=False)
    app.processEvents()
    _verify_connection_manager(window)

    ensure_instrument_api_registered(window.graph)
    app.processEvents()
    _run_cycle(window, DEFAULT_EXPORT_PATH)

    branch_export_path = DEFAULT_EXPORT_PATH.with_name("sample_branch_export.py")
    window.build_branch_sample_flow(prompt_if_dirty=False)
    app.processEvents()
    _run_cycle(window, branch_export_path)

    while_export_path = DEFAULT_EXPORT_PATH.with_name("sample_while_export.py")
    window.build_while_sample_flow(prompt_if_dirty=False)
    app.processEvents()
    _run_cycle(window, while_export_path)

    dpg_export_path = DEFAULT_EXPORT_PATH.with_name("sample_dpg_export.py")
    window.build_digital_pattern_sample_flow(prompt_if_dirty=False)
    app.processEvents()
    _run_cycle(window, dpg_export_path)

    serial_export_path = DEFAULT_EXPORT_PATH.with_name("sample_serial_export.py")
    window.build_serial_sample_flow(prompt_if_dirty=False)
    app.processEvents()
    _run_cycle(window, serial_export_path)

    _verify_headless_subprocess_runner(DEFAULT_FLOW_PATH)
    _verify_debug_session(window, app)
    window.log("all", "子进程运行器与调试单步闭环验证通过。")

    window.log(
        "all",
        f"Smoke test passed -> {DEFAULT_FLOW_PATH} / {DEFAULT_EXPORT_PATH} / {branch_export_path} / "
        f"{while_export_path} / {dpg_export_path} / {serial_export_path}",
    )
    window.close()
    app.processEvents()
    print("demo_02: headless smoke test passed", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo 02 instrument flow programming app")
    parser.add_argument(
        HEADLESS_SMOKE_FLAG,
        action="store_true",
        help="Run validation, execute sample flow, save/load, export, and run exported Python.",
    )
    args = parser.parse_args()

    ensure_assets()

    if args.headless_smoke_test:
        return run_headless_smoke_test()

    app = create_qapplication()
    window = Demo02Window()
    window.show()
    return run_qt_app(app)


if __name__ == "__main__":
    raise SystemExit(main())

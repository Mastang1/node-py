from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

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
        result = window.run_flow()
        if result is None:
            raise RuntimeError("Smoke test failed: runtime returned None.")

        exported_path = window.export_python(export_path)
        if exported_path is None:
            raise RuntimeError("Smoke test failed: export path is None.")

        window.load_flow_from_path(flow_path)
        if not window.validate_flow():
            raise RuntimeError("Smoke test failed: validation after reload did not pass.")

        subprocess.run(
            [sys.executable, str(exported_path)],
            cwd=str(exported_path.parent),
            check=True,
            text=True,
        )

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

    window.log(
        "all",
        f"Smoke test passed -> {DEFAULT_FLOW_PATH} / {DEFAULT_EXPORT_PATH} / {branch_export_path} / "
        f"{while_export_path} / {dpg_export_path} / {serial_export_path}",
    )
    window.close()
    app.processEvents()
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

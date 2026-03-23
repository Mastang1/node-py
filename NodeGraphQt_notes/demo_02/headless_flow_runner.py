"""
CLI entry: run a saved flow JSON in a separate process (Qt + NodeGraphQt).

Usage (from ``NodeGraphQt_notes`` directory)::

    python -m demo_02.headless_flow_runner run path/to/flow.json --lang zh
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
NOTES_DIR = THIS.parent.parent
if str(NOTES_DIR) not in sys.path:
    sys.path.insert(0, str(NOTES_DIR))
NODEGRAPH_ROOT = NOTES_DIR.parent / "NodeGraphQt"
if str(NODEGRAPH_ROOT) not in sys.path:
    sys.path.insert(0, str(NODEGRAPH_ROOT))

from NodeGraphQt import NodeGraph
from Qt import QtWidgets

from demo_02.common import LANG_EN, LANG_ZH
from demo_02.node_registry import (
    configure_graph_port_constraints,
    ensure_instrument_api_registered,
    register_all_nodes,
)
from demo_02.workflow_runtime import WorkflowRuntime


def run_session(json_path: Path, language: str) -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    graph = NodeGraph()
    register_all_nodes(graph)
    ensure_instrument_api_registered(graph)
    graph.set_acyclic(False)
    graph.load_session(str(json_path))
    configure_graph_port_constraints(graph)

    def log_cb(channel: str, message: str) -> None:
        if os.environ.get("DEMO02_QUIET_SMOKE") == "1":
            return
        print(
            json.dumps({"type": "log", "channel": channel, "message": message}, ensure_ascii=False),
            flush=True,
        )

    try:
        runtime = WorkflowRuntime(graph, log_cb, language=language)
        result = runtime.execute()
        print(
            json.dumps(
                {
                    "type": "result",
                    "ok": True,
                    "return_value_repr": repr(result.context.return_value),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 0
    except Exception as exc:
        print(json.dumps({"type": "result", "ok": False, "message": str(exc)}, ensure_ascii=False), flush=True)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless demo_02 flow runner")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run_p = sub.add_parser("run")
    run_p.add_argument("json_path", type=Path)
    run_p.add_argument("--lang", choices=[LANG_ZH, LANG_EN], default=LANG_ZH)
    args = parser.parse_args()
    if args.cmd == "run":
        return run_session(args.json_path, args.lang)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

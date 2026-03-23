"""Console output for simulated instruments; optional silence during headless smoke."""
from __future__ import annotations

import os


def iv_print(message: str) -> None:
    if os.environ.get("DEMO02_QUIET_SMOKE") == "1":
        return
    print(message)

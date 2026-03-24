"""NODE FLOW → linear Python (visit order). Rename run_flow() in your tests."""
from __future__ import annotations

from typing import Any

from demo_02.Instruments_pythonic.general import return_value


def run_flow() -> Any:
    """Instrument API call sequence from the graph (minimal linear form)."""
    variables: dict[str, Any] = {}
    sessions: dict[str, Any] = {}
    _last: Any = None

    _last = True
    _last = 2
    # TODO: control node while_loop — flatten if/while/for manually
    # TODO: control node blocking_delay_loop — flatten if/while/for manually
    return return_value(_last)


# __DEMO02_EXPORT_IMPORTS__
# (copy imports above into your module if you paste only the function body)
# __DEMO02_EXPORT_IMPORTS_END__


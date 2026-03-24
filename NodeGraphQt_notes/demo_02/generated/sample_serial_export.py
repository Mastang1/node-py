"""NODE FLOW → linear Python (visit order). Rename run_flow() in your tests."""
from __future__ import annotations

from typing import Any

from demo_02.Instruments_pythonic.general import return_value

from demo_02.Instruments_pythonic.multi_serial_card import SimMultiSerialCardIvi


def run_flow() -> Any:
    """Instrument API call sequence from the graph (minimal linear form)."""
    variables: dict[str, Any] = {}
    sessions: dict[str, Any] = {}
    _last: Any = None

    _api_SimMultiSerialCardIvi = SimMultiSerialCardIvi()
    _last = _api_SimMultiSerialCardIvi.initialize(resource_name='PCI::SERIAL-CARD-01', id_query=True, reset=False)
    _last = _api_SimMultiSerialCardIvi.self_test(handle='')
    # TODO: 拆包串口自检 (LastResultIndexNode) — linear export not mapped
    # TODO: 写回串口自检 (WriteVariableFromInputNode) — linear export not mapped
    _last = '*IDN?'
    _last = _api_SimMultiSerialCardIvi.open_port(handle='', channel='CH1', port_name='COM1', baud_rate=115200, data_bits=8, parity='N', stop_bits=1, timeout=1.0)
    _last = _api_SimMultiSerialCardIvi.write(handle='', channel='CH1', data='*IDN?', encoding='utf-8')
    _last = _api_SimMultiSerialCardIvi.read(handle='', channel='CH1', size=0, timeout=1.0)
    # TODO: 写回串口回复 (WriteVariableFromInputNode) — linear export not mapped
    _last = _api_SimMultiSerialCardIvi.close_port(handle='', channel='CH1')
    _last = _api_SimMultiSerialCardIvi.close(handle='')
    return return_value(variables.get('serial_reply'))


# __DEMO02_EXPORT_IMPORTS__
# (copy imports above into your module if you paste only the function body)
# __DEMO02_EXPORT_IMPORTS_END__


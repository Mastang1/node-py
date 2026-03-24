"""NODE FLOW → linear Python (visit order). Rename run_flow() in your tests."""
from __future__ import annotations

from typing import Any

from demo_02.Instruments_pythonic.general import return_value, set_variable

from demo_02.Instruments_pythonic.signal_generator import SimSignalGeneratorIvi


def run_flow() -> Any:
    """Instrument API call sequence from the graph (minimal linear form)."""
    variables: dict[str, Any] = {}
    sessions: dict[str, Any] = {}
    _last: Any = None

    set_variable(variables, 'loop_count', 3)
    _last = variables['loop_count']
    _last = variables.get('loop_count', 1)
    _api_SimSignalGeneratorIvi = SimSignalGeneratorIvi()
    _last = _api_SimSignalGeneratorIvi.initialize(resource_name='TCPIP0::192.168.0.10::INSTR', id_query=True, reset=False)
    _last = _api_SimSignalGeneratorIvi.self_test(handle='')
    # TODO: 拆包自检信息 (LastResultIndexNode) — linear export not mapped
    # TODO: 写回自检信息 (WriteVariableFromInputNode) — linear export not mapped
    _last = 0.25
    # TODO: control node for_range — flatten if/while/for manually
    _last = 0.0 + 0.0
    _last = _api_SimSignalGeneratorIvi.configure_waveform(handle='', channel='CH1', waveform='SINE', frequency=1000.0, amplitude=2.0, offset=0.0, phase=0.0)
    # TODO: control node blocking_delay_loop — flatten if/while/for manually
    _last = _api_SimSignalGeneratorIvi.get_identity()
    # TODO: 写回身份变量 (WriteVariableFromInputNode) — linear export not mapped
    return return_value(variables.get('sg_identity'))


# __DEMO02_EXPORT_IMPORTS__
# (copy imports above into your module if you paste only the function body)
# __DEMO02_EXPORT_IMPORTS_END__


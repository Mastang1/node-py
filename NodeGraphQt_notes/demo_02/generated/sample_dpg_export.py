"""NODE FLOW → linear Python (visit order). Rename run_flow() in your tests."""
from __future__ import annotations

from typing import Any

from demo_02.Instruments_pythonic.general import return_value

from demo_02.Instruments_pythonic.digital_pattern_generator import SimDigitalPatternGeneratorIvi


def run_flow() -> Any:
    """Instrument API call sequence from the graph (minimal linear form)."""
    variables: dict[str, Any] = {}
    sessions: dict[str, Any] = {}
    _last: Any = None

    _api_SimDigitalPatternGeneratorIvi = SimDigitalPatternGeneratorIvi()
    _last = _api_SimDigitalPatternGeneratorIvi.initialize(resource_name='PXI0::20-0.0::INSTR', id_query=True, reset=False)
    _last = _api_SimDigitalPatternGeneratorIvi.self_test(handle='')
    # TODO: 拆包自检消息 (LastResultIndexNode) — linear export not mapped
    # TODO: 写回自检消息 (WriteVariableFromInputNode) — linear export not mapped
    _last = _api_SimDigitalPatternGeneratorIvi.configure_timing(handle='', sample_rate=1000000.0, logic_level='3.3V')
    _last = _api_SimDigitalPatternGeneratorIvi.load_pattern(handle='', pattern_name='burst_A', pattern_bits='101100111000', loop_count=2)
    _last = _api_SimDigitalPatternGeneratorIvi.start_output(handle='')
    _last = _api_SimDigitalPatternGeneratorIvi.query_status(handle='')
    # TODO: 写回时序摘要 (WriteVariableFromInputNode) — linear export not mapped
    _last = _api_SimDigitalPatternGeneratorIvi.stop_output(handle='')
    _last = _api_SimDigitalPatternGeneratorIvi.close(handle='')
    return return_value(variables.get('dpg_timing'))


# __DEMO02_EXPORT_IMPORTS__
# (copy imports above into your module if you paste only the function body)
# __DEMO02_EXPORT_IMPORTS_END__


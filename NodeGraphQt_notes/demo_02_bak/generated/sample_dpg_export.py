from __future__ import annotations
import sys
from pathlib import Path
BASE_DIR = Path(r'F:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02')
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from common import as_bool, as_float, as_int, as_text
from Instruments_pythonic.digital_pattern_generator import SimDigitalPatternGeneratorIvi
def node_0x28b017de600(context):
    # 配置时序 (ApiNodeSimDigitalPatternGeneratorIviConfiguretiming)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_sample_rate = _read_input_value(context, None, 1000000.0)
    sample_rate = as_float(raw_sample_rate)
    raw_logic_level = _read_input_value(context, None, '3.3V')
    logic_level = as_text(raw_logic_level)
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.configure_timing(handle=handle, sample_rate=sample_rate, logic_level=logic_level)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b017de600', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['configure_timing.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b019e8e00(context):
    # 加载模式 (ApiNodeSimDigitalPatternGeneratorIviLoadpattern)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_pattern_name = _read_input_value(context, None, 'burst_A')
    pattern_name = as_text(raw_pattern_name)
    raw_pattern_bits = _read_input_value(context, None, '101100111000')
    pattern_bits = as_text(raw_pattern_bits)
    raw_loop_count = _read_input_value(context, None, 2)
    loop_count = as_int(raw_loop_count)
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.load_pattern(handle=handle, pattern_name=pattern_name, pattern_bits=pattern_bits, loop_count=loop_count)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b019e8e00', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['load_pattern.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b017dfb60(context):
    # 开始输出 (ApiNodeSimDigitalPatternGeneratorIviStartoutput)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.start_output(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b017dfb60', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['start_output.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b01737ad0(context):
    # 开始 (StartNode)
    print('[Start] Demo 02 数字模式发生器动态流程')
    context['last_result'] = 'Demo 02 数字模式发生器动态流程'
    return 'flow_out'
def node_0x28b019d0110(context):
    # 初始化数字模式发生器 (ApiNodeSimDigitalPatternGeneratorIviInitialize)
    raw_resource_name = _read_input_value(context, None, 'PXI0::20-0.0::INSTR')
    resource_name = as_text(raw_resource_name)
    raw_id_query = _read_input_value(context, None, True)
    id_query = as_bool(raw_id_query)
    raw_reset = _read_input_value(context, None, False)
    reset = as_bool(raw_reset)
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.initialize(resource_name=resource_name, id_query=id_query, reset=reset)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_handle = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b019d0110', 'handle', value_handle)
    context['variables']['handle'] = value_handle
    context['variables']['initialize.handle'] = value_handle
    value_identity = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b019d0110', 'identity', value_identity)
    context['variables']['identity'] = value_identity
    context['variables']['initialize.identity'] = value_identity
    context['last_result'] = [context['variables']['handle'], context['variables']['identity']]
    return 'flow_out'
def node_0x28b017df800(context):
    # 数字模式自检 (ApiNodeSimDigitalPatternGeneratorIviSelftest)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.self_test(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_code = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b017df800', 'code', value_code)
    context['variables']['code'] = value_code
    context['variables']['self_test.code'] = value_code
    value_message = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b017df800', 'message', value_message)
    context['variables']['message'] = value_message
    context['variables']['self_test.message'] = value_message
    context['last_result'] = [context['variables']['code'], context['variables']['message']]
    return 'flow_out'
def node_0x28b017ddc70(context):
    # 拆包自检消息 (LastResultIndexNode)
    unpacked_value = 'dpg_self_test_missing'
    if isinstance(context.get('last_result'), (list, tuple)):
        if 0 <= 1 < len(context['last_result']):
            unpacked_value = context['last_result'][1]
    _set_output_value(context, '0x28b017ddc70', 'value', unpacked_value)
    context['last_result'] = unpacked_value
    return 'flow_out'
def node_0x28b019e9970(context):
    # 写回自检消息 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x28b017ddc70', 'value'), '')
    context['variables']['dpg_self_test'] = input_value
    _set_output_value(context, '0x28b019e9970', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x28b028ebf50(context):
    # 查询状态 (ApiNodeSimDigitalPatternGeneratorIviQuerystatus)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.query_status(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_running = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b028ebf50', 'running', value_running)
    context['variables']['running'] = value_running
    context['variables']['query_status.running'] = value_running
    value_timing = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b028ebf50', 'timing', value_timing)
    context['variables']['timing'] = value_timing
    context['variables']['query_status.timing'] = value_timing
    value_pattern_loaded = result_list[2] if len(result_list) > 2 else None
    _set_output_value(context, '0x28b028ebf50', 'pattern_loaded', value_pattern_loaded)
    context['variables']['pattern_loaded'] = value_pattern_loaded
    context['variables']['query_status.pattern_loaded'] = value_pattern_loaded
    context['last_result'] = [context['variables']['running'], context['variables']['timing'], context['variables']['pattern_loaded']]
    return 'flow_out'
def node_0x28b028eaf00(context):
    # 写回时序摘要 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x28b028ebf50', 'timing'), '')
    context['variables']['dpg_timing'] = input_value
    _set_output_value(context, '0x28b028eaf00', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x28b019e8800(context):
    # 停止输出 (ApiNodeSimDigitalPatternGeneratorIviStopoutput)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.stop_output(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b019e8800', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['stop_output.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b028e8350(context):
    # 关闭数字模式会话 (ApiNodeSimDigitalPatternGeneratorIviClose)
    raw_handle = _read_input_value(context, ('0x28b019d0110', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi') or SimDigitalPatternGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.digital_pattern_generator:SimDigitalPatternGeneratorIvi'] = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_digital_pattern_generator_SimDigitalPatternGeneratorIvi.close(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b028e8350', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['close_session.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b019e9a30(context):
    # 返回 (ReturnNode)
    context['return_value'] = context['variables'].get('dpg_timing')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
START_NODE_ID = '0x28b01737ad0'
FLOW_LINKS = {'0x28b017de600': {'flow_out': '0x28b019e8e00'}, '0x28b019e8e00': {'flow_out': '0x28b017dfb60'}, '0x28b017dfb60': {'flow_out': '0x28b028ebf50'}, '0x28b01737ad0': {'flow_out': '0x28b019d0110'}, '0x28b019d0110': {'flow_out': '0x28b017df800'}, '0x28b017df800': {'flow_out': '0x28b017ddc70'}, '0x28b017ddc70': {'flow_out': '0x28b019e9970'}, '0x28b019e9970': {'flow_out': '0x28b017de600'}, '0x28b028ebf50': {'flow_out': '0x28b028eaf00'}, '0x28b028eaf00': {'flow_out': '0x28b019e8800'}, '0x28b019e8800': {'flow_out': '0x28b028e8350'}, '0x28b028e8350': {'flow_out': '0x28b019e9a30'}, '0x28b019e9a30': {}}
UNREACHABLE_NODES = []
NODE_NAMES = {
    '0x28b017de600': '配置时序',
    '0x28b019e8e00': '加载模式',
    '0x28b017dfb60': '开始输出',
    '0x28b01737ad0': '开始',
    '0x28b019d0110': '初始化数字模式发生器',
    '0x28b017df800': '数字模式自检',
    '0x28b017ddc70': '拆包自检消息',
    '0x28b019e9970': '写回自检消息',
    '0x28b028ebf50': '查询状态',
    '0x28b028eaf00': '写回时序摘要',
    '0x28b019e8800': '停止输出',
    '0x28b028e8350': '关闭数字模式会话',
    '0x28b019e9a30': '返回',
}
def _read_input_value(context, source, fallback=None):
    if source is None:
        return fallback
    source_key = tuple(source)
    if source_key not in context['port_values']:
        raise RuntimeError(f'Upstream data not ready: {source_key[0]}:{source_key[1]}')
    return context['port_values'][source_key]
def _set_output_value(context, node_id, key, value):
    context['port_values'][(node_id, key)] = value
    return value
NODE_DISPATCH = {
    '0x28b017de600': node_0x28b017de600,
    '0x28b019e8e00': node_0x28b019e8e00,
    '0x28b017dfb60': node_0x28b017dfb60,
    '0x28b01737ad0': node_0x28b01737ad0,
    '0x28b019d0110': node_0x28b019d0110,
    '0x28b017df800': node_0x28b017df800,
    '0x28b017ddc70': node_0x28b017ddc70,
    '0x28b019e9970': node_0x28b019e9970,
    '0x28b028ebf50': node_0x28b028ebf50,
    '0x28b028eaf00': node_0x28b028eaf00,
    '0x28b019e8800': node_0x28b019e8800,
    '0x28b028e8350': node_0x28b028e8350,
    '0x28b019e9a30': node_0x28b019e9a30,
}
def run_flow(context=None):
    if context is None:
        context = {}
    context.setdefault('sessions', {})
    context.setdefault('api_instances', {})
    context.setdefault('variables', {})
    context.setdefault('logs', [])
    context.setdefault('last_result', None)
    context.setdefault('return_value', None)
    context.setdefault('port_values', {})
    context.setdefault('loop_states', {})
    context.setdefault('terminated', False)
    print('[Exported Flow] start')
    if UNREACHABLE_NODES:
        print('[Warning] unreachable nodes:', ', '.join(UNREACHABLE_NODES))
    current_node_id = START_NODE_ID
    step_count = 0
    try:
        while current_node_id:
            step_count += 1
            if step_count > 10000:
                raise RuntimeError('Flow exceeded 10000 execution steps.')
            print(f"[Exported Flow] node -> {NODE_NAMES.get(current_node_id, current_node_id)}")
            next_flow_key = NODE_DISPATCH[current_node_id](context)
            if context.get('terminated'):
                break
            current_node_id = FLOW_LINKS.get(current_node_id, {}).get(next_flow_key)
        print('[Exported Flow] done')
        return context.get('return_value', context.get('last_result'))
    finally:
        for session_name, session in list(context['sessions'].items()):
            if getattr(session, 'initialized', False):
                session.close()
                print(f'[Exported Flow] auto close session: {session_name}')
def main():
    result = run_flow()
    print('[Exported Flow] return ->', result)
if __name__ == '__main__':
    main()

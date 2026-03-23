from __future__ import annotations
import sys
from pathlib import Path
BASE_DIR = Path(r'F:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02')
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from common import as_bool, as_float, as_int, as_text
from Instruments_pythonic import general as general_helpers
from Instruments_pythonic.signal_generator import SimSignalGeneratorIvi
def node_0x28b01aec6e0(context):
    # 相位偏移 (FloatConstantNode)
    _set_output_value(context, '0x28b01aec6e0', 'value', 0.25)
    context['last_result'] = 0.25
    return 'flow_out'
def node_0x28b01aec260(context):
    # 相位计算 (MathBinaryNode)
    left_value = as_float(_read_input_value(context, ('0x28b019e2f60', 'current_value'), 0.0))
    right_value = as_float(_read_input_value(context, ('0x28b01aec6e0', 'value'), 0.0))
    math_result = left_value + right_value
    _set_output_value(context, '0x28b01aec260', 'result', math_result)
    context['last_result'] = math_result
    return 'flow_out'
def node_0x28b0192c9b0(context):
    # 动态配置波形 (ApiNodeSimSignalGeneratorIviConfigurewaveform)
    raw_handle = _read_input_value(context, ('0x28b019e3fb0', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_channel = _read_input_value(context, None, 'CH1')
    channel = as_text(raw_channel)
    raw_waveform = _read_input_value(context, None, 'SINE')
    waveform = as_text(raw_waveform)
    raw_frequency = _read_input_value(context, None, 1000.0)
    frequency = as_float(raw_frequency)
    raw_amplitude = _read_input_value(context, None, 2.0)
    amplitude = as_float(raw_amplitude)
    raw_offset = _read_input_value(context, None, 0.0)
    offset = as_float(raw_offset)
    raw_phase = _read_input_value(context, ('0x28b01aec260', 'result'), 0.0)
    phase = as_float(raw_phase)
    session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi') or SimSignalGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi'] = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi.configure_waveform(handle=handle, channel=channel, waveform=waveform, frequency=frequency, amplitude=amplitude, offset=offset, phase=phase)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b0192c9b0', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['configure_waveform.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b01799f40(context):
    # 阻塞延时循环 (ApiNodeGeneralFlowApiBlockingdelayloop)
    raw_seconds = _read_input_value(context, None, 0.01)
    seconds = as_float(raw_seconds)
    raw_loops = _read_input_value(context, None, 1)
    loops = as_int(raw_loops)
    total_delay = 0.0
    for _ in range(max(0, as_int(loops))):
        general_helpers.delay(max(0.0, as_float(seconds)))
        total_delay += max(0.0, as_float(seconds))
    _set_output_value(context, '0x28b01799f40', 'total_delay', total_delay)
    context['last_result'] = total_delay
    return 'flow_out'
def node_0x28b01772090(context):
    # 开始 (StartNode)
    print('[Start] Demo 02 动态 API 控制流')
    context['last_result'] = 'Demo 02 动态 API 控制流'
    return 'flow_out'
def node_0x28b019e1430(context):
    # 设置循环次数 (SetVariableNode)
    general_helpers.set_variable(context['variables'], 'loop_count', 3)
    context['last_result'] = context['variables']['loop_count']
    return 'flow_out'
def node_0x28b019e2990(context):
    # 读取循环次数 (ReadIntVariableNode)
    variable_value = as_int(context['variables'].get('loop_count', 1))
    _set_output_value(context, '0x28b019e2990', 'value', variable_value)
    context['last_result'] = variable_value
    return 'flow_out'
def node_0x28b019e3fb0(context):
    # 初始化信号源 (ApiNodeSimSignalGeneratorIviInitialize)
    raw_resource_name = _read_input_value(context, None, 'TCPIP0::192.168.0.10::INSTR')
    resource_name = as_text(raw_resource_name)
    raw_id_query = _read_input_value(context, None, True)
    id_query = as_bool(raw_id_query)
    raw_reset = _read_input_value(context, None, False)
    reset = as_bool(raw_reset)
    session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi') or SimSignalGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi'] = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi.initialize(resource_name=resource_name, id_query=id_query, reset=reset)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_handle = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b019e3fb0', 'handle', value_handle)
    context['variables']['handle'] = value_handle
    context['variables']['initialize.handle'] = value_handle
    value_identity = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b019e3fb0', 'identity', value_identity)
    context['variables']['identity'] = value_identity
    context['variables']['initialize.identity'] = value_identity
    context['last_result'] = [context['variables']['handle'], context['variables']['identity']]
    return 'flow_out'
def node_0x28b019e8260(context):
    # 信号源自检 (ApiNodeSimSignalGeneratorIviSelftest)
    raw_handle = _read_input_value(context, ('0x28b019e3fb0', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi') or SimSignalGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi'] = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi.self_test(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_code = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b019e8260', 'code', value_code)
    context['variables']['code'] = value_code
    context['variables']['self_test.code'] = value_code
    value_message = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b019e8260', 'message', value_message)
    context['variables']['message'] = value_message
    context['variables']['self_test.message'] = value_message
    context['last_result'] = [context['variables']['code'], context['variables']['message']]
    return 'flow_out'
def node_0x28b019e8500(context):
    # 拆包自检信息 (LastResultIndexNode)
    unpacked_value = 'self_test_missing'
    if isinstance(context.get('last_result'), (list, tuple)):
        if 0 <= 1 < len(context['last_result']):
            unpacked_value = context['last_result'][1]
    _set_output_value(context, '0x28b019e8500', 'value', unpacked_value)
    context['last_result'] = unpacked_value
    return 'flow_out'
def node_0x28b019eb560(context):
    # 写回自检信息 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x28b019e8500', 'value'), 'fallback_self_test')
    context['variables']['self_test_message'] = input_value
    _set_output_value(context, '0x28b019eb560', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x28b019e2f60(context):
    # FOR 循环 (ApiNodeGeneralFlowApiForrange)
    raw_value = _read_input_value(context, ('0x28b019e2990', 'value'), 1)
    value = as_int(raw_value)
    state = context.setdefault('loop_states', {}).setdefault('0x28b019e2f60', {'index': 0})
    total_iterations = max(0, as_int(value))
    if state['index'] < total_iterations:
        current_value = state['index']
        state['index'] += 1
        _set_output_value(context, '0x28b019e2f60', 'current_value', current_value)
        _set_output_value(context, '0x28b019e2f60', 'current_index', current_value)
        context['last_result'] = current_value
        return 'loop_body'
    state['index'] = 0
    context['last_result'] = total_iterations
    return 'completed'
def node_0x28b019e8650(context):
    # 读取身份 (ApiNodeSimSignalGeneratorIviGetidentity)
    session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi') or SimSignalGeneratorIvi()
    context['api_instances']['demo_02.Instruments_pythonic.signal_generator:SimSignalGeneratorIvi'] = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi
    result_list = session_demo_02_Instruments_pythonic_signal_generator_SimSignalGeneratorIvi.get_identity()
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_identity = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b019e8650', 'identity', value_identity)
    context['variables']['identity'] = value_identity
    context['variables']['get_identity.identity'] = value_identity
    context['last_result'] = context['variables']['identity']
    return 'flow_out'
def node_0x28b01af4140(context):
    # 写回身份变量 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x28b019e8650', 'identity'), '')
    context['variables']['sg_identity'] = input_value
    _set_output_value(context, '0x28b01af4140', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x28b01af54c0(context):
    # 返回 (ReturnNode)
    context['return_value'] = context['variables'].get('sg_identity')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
START_NODE_ID = '0x28b01772090'
FLOW_LINKS = {'0x28b01aec6e0': {'flow_out': '0x28b019e2f60'}, '0x28b01aec260': {'flow_out': '0x28b0192c9b0'}, '0x28b0192c9b0': {'flow_out': '0x28b01799f40'}, '0x28b01799f40': {'flow_out': '0x28b019e2f60'}, '0x28b01772090': {'flow_out': '0x28b019e1430'}, '0x28b019e1430': {'flow_out': '0x28b019e2990'}, '0x28b019e2990': {'flow_out': '0x28b019e3fb0'}, '0x28b019e3fb0': {'flow_out': '0x28b019e8260'}, '0x28b019e8260': {'flow_out': '0x28b019e8500'}, '0x28b019e8500': {'flow_out': '0x28b019eb560'}, '0x28b019eb560': {'flow_out': '0x28b01aec6e0'}, '0x28b019e2f60': {'loop_body': '0x28b01aec260', 'completed': '0x28b019e8650'}, '0x28b019e8650': {'flow_out': '0x28b01af4140'}, '0x28b01af4140': {'flow_out': '0x28b01af54c0'}, '0x28b01af54c0': {}}
UNREACHABLE_NODES = []
NODE_NAMES = {
    '0x28b01aec6e0': '相位偏移',
    '0x28b01aec260': '相位计算',
    '0x28b0192c9b0': '动态配置波形',
    '0x28b01799f40': '阻塞延时循环',
    '0x28b01772090': '开始',
    '0x28b019e1430': '设置循环次数',
    '0x28b019e2990': '读取循环次数',
    '0x28b019e3fb0': '初始化信号源',
    '0x28b019e8260': '信号源自检',
    '0x28b019e8500': '拆包自检信息',
    '0x28b019eb560': '写回自检信息',
    '0x28b019e2f60': 'FOR 循环',
    '0x28b019e8650': '读取身份',
    '0x28b01af4140': '写回身份变量',
    '0x28b01af54c0': '返回',
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
    '0x28b01aec6e0': node_0x28b01aec6e0,
    '0x28b01aec260': node_0x28b01aec260,
    '0x28b0192c9b0': node_0x28b0192c9b0,
    '0x28b01799f40': node_0x28b01799f40,
    '0x28b01772090': node_0x28b01772090,
    '0x28b019e1430': node_0x28b019e1430,
    '0x28b019e2990': node_0x28b019e2990,
    '0x28b019e3fb0': node_0x28b019e3fb0,
    '0x28b019e8260': node_0x28b019e8260,
    '0x28b019e8500': node_0x28b019e8500,
    '0x28b019eb560': node_0x28b019eb560,
    '0x28b019e2f60': node_0x28b019e2f60,
    '0x28b019e8650': node_0x28b019e8650,
    '0x28b01af4140': node_0x28b01af4140,
    '0x28b01af54c0': node_0x28b01af54c0,
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

from __future__ import annotations
import sys
from pathlib import Path
BASE_DIR = Path(r'F:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02')
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from common import as_bool, as_float, as_int, as_text
from Instruments_pythonic.multi_serial_card import SimMultiSerialCardIvi
def node_0x28b01aec710(context):
    # 打开端口 (ApiNodeSimMultiSerialCardIviOpenport)
    raw_handle = _read_input_value(context, ('0x28b017def00', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_channel = _read_input_value(context, None, 'CH1')
    channel = as_text(raw_channel)
    raw_port_name = _read_input_value(context, None, 'COM1')
    port_name = as_text(raw_port_name)
    raw_baud_rate = _read_input_value(context, None, 115200)
    baud_rate = as_int(raw_baud_rate)
    raw_data_bits = _read_input_value(context, None, 8)
    data_bits = as_int(raw_data_bits)
    raw_parity = _read_input_value(context, None, 'N')
    parity = as_text(raw_parity)
    raw_stop_bits = _read_input_value(context, None, 1)
    stop_bits = as_int(raw_stop_bits)
    raw_timeout = _read_input_value(context, None, 1.0)
    timeout = as_float(raw_timeout)
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.open_port(handle=handle, channel=channel, port_name=port_name, baud_rate=baud_rate, data_bits=data_bits, parity=parity, stop_bits=stop_bits, timeout=timeout)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b01aec710', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['open_port.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b01af4470(context):
    # 写串口 (ApiNodeSimMultiSerialCardIviWrite)
    raw_handle = _read_input_value(context, ('0x28b017def00', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_channel = _read_input_value(context, None, 'CH1')
    channel = as_text(raw_channel)
    raw_data = _read_input_value(context, ('0x28b019cd5b0', 'value'), '*IDN?')
    data = as_text(raw_data)
    raw_encoding = _read_input_value(context, None, 'utf-8')
    encoding = as_text(raw_encoding)
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.write(handle=handle, channel=channel, data=data, encoding=encoding)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_bytes_written = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b01af4470', 'bytes_written', value_bytes_written)
    context['variables']['bytes_written'] = value_bytes_written
    context['variables']['write.bytes_written'] = value_bytes_written
    context['last_result'] = context['variables']['bytes_written']
    return 'flow_out'
def node_0x28b0283ffe0(context):
    # 读串口 (ApiNodeSimMultiSerialCardIviRead)
    raw_handle = _read_input_value(context, ('0x28b017def00', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_channel = _read_input_value(context, None, 'CH1')
    channel = as_text(raw_channel)
    raw_size = _read_input_value(context, None, 0)
    size = as_int(raw_size)
    raw_timeout = _read_input_value(context, None, 1.0)
    timeout = as_float(raw_timeout)
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.read(handle=handle, channel=channel, size=size, timeout=timeout)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_reply = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b0283ffe0', 'reply', value_reply)
    context['variables']['reply'] = value_reply
    context['variables']['read.reply'] = value_reply
    context['last_result'] = context['variables']['reply']
    return 'flow_out'
def node_0x28b017def60(context):
    # 开始 (StartNode)
    print('[Start] Demo 02 串口卡动态流程')
    context['last_result'] = 'Demo 02 串口卡动态流程'
    return 'flow_out'
def node_0x28b017def00(context):
    # 初始化串口卡 (ApiNodeSimMultiSerialCardIviInitialize)
    raw_resource_name = _read_input_value(context, None, 'PCI::SERIAL-CARD-01')
    resource_name = as_text(raw_resource_name)
    raw_id_query = _read_input_value(context, None, True)
    id_query = as_bool(raw_id_query)
    raw_reset = _read_input_value(context, None, False)
    reset = as_bool(raw_reset)
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.initialize(resource_name=resource_name, id_query=id_query, reset=reset)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_handle = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b017def00', 'handle', value_handle)
    context['variables']['handle'] = value_handle
    context['variables']['initialize.handle'] = value_handle
    value_identity = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b017def00', 'identity', value_identity)
    context['variables']['identity'] = value_identity
    context['variables']['initialize.identity'] = value_identity
    context['last_result'] = [context['variables']['handle'], context['variables']['identity']]
    return 'flow_out'
def node_0x28b01798620(context):
    # 串口卡自检 (ApiNodeSimMultiSerialCardIviSelftest)
    raw_handle = _read_input_value(context, ('0x28b017def00', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.self_test(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_code = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b01798620', 'code', value_code)
    context['variables']['code'] = value_code
    context['variables']['self_test.code'] = value_code
    value_message = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x28b01798620', 'message', value_message)
    context['variables']['message'] = value_message
    context['variables']['self_test.message'] = value_message
    context['last_result'] = [context['variables']['code'], context['variables']['message']]
    return 'flow_out'
def node_0x28b01aec650(context):
    # 拆包串口自检 (LastResultIndexNode)
    unpacked_value = 'serial_self_test_missing'
    if isinstance(context.get('last_result'), (list, tuple)):
        if 0 <= 1 < len(context['last_result']):
            unpacked_value = context['last_result'][1]
    _set_output_value(context, '0x28b01aec650', 'value', unpacked_value)
    context['last_result'] = unpacked_value
    return 'flow_out'
def node_0x28b019cdf40(context):
    # 写回串口自检 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x28b01aec650', 'value'), '')
    context['variables']['serial_self_test'] = input_value
    _set_output_value(context, '0x28b019cdf40', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x28b019cd5b0(context):
    # 串口发送文本 (TextConstantNode)
    _set_output_value(context, '0x28b019cd5b0', 'value', '*IDN?')
    context['last_result'] = '*IDN?'
    return 'flow_out'
def node_0x28b01af4890(context):
    # 写回串口回复 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x28b0283ffe0', 'reply'), '')
    context['variables']['serial_reply'] = input_value
    _set_output_value(context, '0x28b01af4890', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x28b028e9c70(context):
    # 关闭端口 (ApiNodeSimMultiSerialCardIviCloseport)
    raw_handle = _read_input_value(context, ('0x28b017def00', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_channel = _read_input_value(context, None, 'CH1')
    channel = as_text(raw_channel)
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.close_port(handle=handle, channel=channel)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b028e9c70', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['close_port.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b01771f70(context):
    # 关闭串口会话 (ApiNodeSimMultiSerialCardIviClose)
    raw_handle = _read_input_value(context, ('0x28b017def00', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi = context.setdefault('api_instances', {}).get('demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi') or SimMultiSerialCardIvi()
    context['api_instances']['demo_02.Instruments_pythonic.multi_serial_card:SimMultiSerialCardIvi'] = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi
    result_list = session_demo_02_Instruments_pythonic_multi_serial_card_SimMultiSerialCardIvi.close(handle=handle)
    if result_list is None:
        result_list = []
    elif not isinstance(result_list, (list, tuple)):
        result_list = [result_list]
    else:
        result_list = list(result_list)
    value_status = result_list[0] if len(result_list) > 0 else None
    _set_output_value(context, '0x28b01771f70', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['close.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x28b01af4050(context):
    # 返回 (ReturnNode)
    context['return_value'] = context['variables'].get('serial_reply')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
START_NODE_ID = '0x28b017def60'
FLOW_LINKS = {'0x28b01aec710': {'flow_out': '0x28b01af4470'}, '0x28b01af4470': {'flow_out': '0x28b0283ffe0'}, '0x28b0283ffe0': {'flow_out': '0x28b01af4890'}, '0x28b017def60': {'flow_out': '0x28b017def00'}, '0x28b017def00': {'flow_out': '0x28b01798620'}, '0x28b01798620': {'flow_out': '0x28b01aec650'}, '0x28b01aec650': {'flow_out': '0x28b019cdf40'}, '0x28b019cdf40': {'flow_out': '0x28b019cd5b0'}, '0x28b019cd5b0': {'flow_out': '0x28b01aec710'}, '0x28b01af4890': {'flow_out': '0x28b028e9c70'}, '0x28b028e9c70': {'flow_out': '0x28b01771f70'}, '0x28b01771f70': {'flow_out': '0x28b01af4050'}, '0x28b01af4050': {}}
UNREACHABLE_NODES = []
NODE_NAMES = {
    '0x28b01aec710': '打开端口',
    '0x28b01af4470': '写串口',
    '0x28b0283ffe0': '读串口',
    '0x28b017def60': '开始',
    '0x28b017def00': '初始化串口卡',
    '0x28b01798620': '串口卡自检',
    '0x28b01aec650': '拆包串口自检',
    '0x28b019cdf40': '写回串口自检',
    '0x28b019cd5b0': '串口发送文本',
    '0x28b01af4890': '写回串口回复',
    '0x28b028e9c70': '关闭端口',
    '0x28b01771f70': '关闭串口会话',
    '0x28b01af4050': '返回',
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
    '0x28b01aec710': node_0x28b01aec710,
    '0x28b01af4470': node_0x28b01af4470,
    '0x28b0283ffe0': node_0x28b0283ffe0,
    '0x28b017def60': node_0x28b017def60,
    '0x28b017def00': node_0x28b017def00,
    '0x28b01798620': node_0x28b01798620,
    '0x28b01aec650': node_0x28b01aec650,
    '0x28b019cdf40': node_0x28b019cdf40,
    '0x28b019cd5b0': node_0x28b019cd5b0,
    '0x28b01af4890': node_0x28b01af4890,
    '0x28b028e9c70': node_0x28b028e9c70,
    '0x28b01771f70': node_0x28b01771f70,
    '0x28b01af4050': node_0x28b01af4050,
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

from __future__ import annotations
import sys
from pathlib import Path
BASE_DIR = Path(r'F:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02')
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from common import as_bool, as_float, as_int, as_text
from Instruments_pythonic.multi_serial_card import SimMultiSerialCardIvi
def node_0x1d4c0fe4c20(context):
    # 打开端口 (ApiNodeSimMultiSerialCardIviOpenport)
    raw_handle = _read_input_value(context, ('0x1d4beff7410', 'handle'), '')
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
    _set_output_value(context, '0x1d4c0fe4c20', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['open_port.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x1d4c0fbb200(context):
    # 写串口 (ApiNodeSimMultiSerialCardIviWrite)
    raw_handle = _read_input_value(context, ('0x1d4beff7410', 'handle'), '')
    handle = context['variables'].get(as_text(raw_handle), as_text(raw_handle))
    raw_channel = _read_input_value(context, None, 'CH1')
    channel = as_text(raw_channel)
    raw_data = _read_input_value(context, ('0x1d4beffc1a0', 'value'), '*IDN?')
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
    _set_output_value(context, '0x1d4c0fbb200', 'bytes_written', value_bytes_written)
    context['variables']['bytes_written'] = value_bytes_written
    context['variables']['write.bytes_written'] = value_bytes_written
    context['last_result'] = context['variables']['bytes_written']
    return 'flow_out'
def node_0x1d4beed4c50(context):
    # 读串口 (ApiNodeSimMultiSerialCardIviRead)
    raw_handle = _read_input_value(context, ('0x1d4beff7410', 'handle'), '')
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
    _set_output_value(context, '0x1d4beed4c50', 'reply', value_reply)
    context['variables']['reply'] = value_reply
    context['variables']['read.reply'] = value_reply
    context['last_result'] = context['variables']['reply']
    return 'flow_out'
def node_0x1d4beed6570(context):
    # 开始 (StartNode)
    print('[Start] Demo 02 串口卡动态流程')
    context['last_result'] = 'Demo 02 串口卡动态流程'
    return 'flow_out'
def node_0x1d4beff7410(context):
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
    _set_output_value(context, '0x1d4beff7410', 'handle', value_handle)
    context['variables']['handle'] = value_handle
    context['variables']['initialize.handle'] = value_handle
    value_identity = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x1d4beff7410', 'identity', value_identity)
    context['variables']['identity'] = value_identity
    context['variables']['initialize.identity'] = value_identity
    context['last_result'] = [context['variables']['handle'], context['variables']['identity']]
    return 'flow_out'
def node_0x1d4beed4140(context):
    # 串口卡自检 (ApiNodeSimMultiSerialCardIviSelftest)
    raw_handle = _read_input_value(context, ('0x1d4beff7410', 'handle'), '')
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
    _set_output_value(context, '0x1d4beed4140', 'code', value_code)
    context['variables']['code'] = value_code
    context['variables']['self_test.code'] = value_code
    value_message = result_list[1] if len(result_list) > 1 else None
    _set_output_value(context, '0x1d4beed4140', 'message', value_message)
    context['variables']['message'] = value_message
    context['variables']['self_test.message'] = value_message
    context['last_result'] = [context['variables']['code'], context['variables']['message']]
    return 'flow_out'
def node_0x1d4beffc890(context):
    # 拆包串口自检 (LastResultIndexNode)
    unpacked_value = 'serial_self_test_missing'
    if isinstance(context.get('last_result'), (list, tuple)):
        if 0 <= 1 < len(context['last_result']):
            unpacked_value = context['last_result'][1]
    _set_output_value(context, '0x1d4beffc890', 'value', unpacked_value)
    context['last_result'] = unpacked_value
    return 'flow_out'
def node_0x1d4beffb860(context):
    # 写回串口自检 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x1d4beffc890', 'value'), '')
    context['variables']['serial_self_test'] = input_value
    _set_output_value(context, '0x1d4beffb860', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x1d4beffc1a0(context):
    # 串口发送文本 (TextConstantNode)
    _set_output_value(context, '0x1d4beffc1a0', 'value', '*IDN?')
    context['last_result'] = '*IDN?'
    return 'flow_out'
def node_0x1d4beed4e60(context):
    # 写回串口回复 (WriteVariableFromInputNode)
    input_value = _read_input_value(context, ('0x1d4beed4c50', 'reply'), '')
    context['variables']['serial_reply'] = input_value
    _set_output_value(context, '0x1d4beed4e60', 'value', input_value)
    context['last_result'] = input_value
    return 'flow_out'
def node_0x1d4c0fe4140(context):
    # 关闭端口 (ApiNodeSimMultiSerialCardIviCloseport)
    raw_handle = _read_input_value(context, ('0x1d4beff7410', 'handle'), '')
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
    _set_output_value(context, '0x1d4c0fe4140', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['close_port.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x1d4beffc470(context):
    # 关闭串口会话 (ApiNodeSimMultiSerialCardIviClose)
    raw_handle = _read_input_value(context, ('0x1d4beff7410', 'handle'), '')
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
    _set_output_value(context, '0x1d4beffc470', 'status', value_status)
    context['variables']['status'] = value_status
    context['variables']['close.status'] = value_status
    context['last_result'] = context['variables']['status']
    return 'flow_out'
def node_0x1d4c0fba750(context):
    # 返回 (ReturnNode)
    context['return_value'] = context['variables'].get('serial_reply')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
START_NODE_ID = '0x1d4beed6570'
FLOW_LINKS = {'0x1d4c0fe4c20': {'flow_out': '0x1d4c0fbb200'}, '0x1d4c0fbb200': {'flow_out': '0x1d4beed4c50'}, '0x1d4beed4c50': {'flow_out': '0x1d4beed4e60'}, '0x1d4beed6570': {'flow_out': '0x1d4beff7410'}, '0x1d4beff7410': {'flow_out': '0x1d4beed4140'}, '0x1d4beed4140': {'flow_out': '0x1d4beffc890'}, '0x1d4beffc890': {'flow_out': '0x1d4beffb860'}, '0x1d4beffb860': {'flow_out': '0x1d4beffc1a0'}, '0x1d4beffc1a0': {'flow_out': '0x1d4c0fe4c20'}, '0x1d4beed4e60': {'flow_out': '0x1d4c0fe4140'}, '0x1d4c0fe4140': {'flow_out': '0x1d4beffc470'}, '0x1d4beffc470': {'flow_out': '0x1d4c0fba750'}, '0x1d4c0fba750': {}}
UNREACHABLE_NODES = []
NODE_NAMES = {
    '0x1d4c0fe4c20': '打开端口',
    '0x1d4c0fbb200': '写串口',
    '0x1d4beed4c50': '读串口',
    '0x1d4beed6570': '开始',
    '0x1d4beff7410': '初始化串口卡',
    '0x1d4beed4140': '串口卡自检',
    '0x1d4beffc890': '拆包串口自检',
    '0x1d4beffb860': '写回串口自检',
    '0x1d4beffc1a0': '串口发送文本',
    '0x1d4beed4e60': '写回串口回复',
    '0x1d4c0fe4140': '关闭端口',
    '0x1d4beffc470': '关闭串口会话',
    '0x1d4c0fba750': '返回',
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
    '0x1d4c0fe4c20': node_0x1d4c0fe4c20,
    '0x1d4c0fbb200': node_0x1d4c0fbb200,
    '0x1d4beed4c50': node_0x1d4beed4c50,
    '0x1d4beed6570': node_0x1d4beed6570,
    '0x1d4beff7410': node_0x1d4beff7410,
    '0x1d4beed4140': node_0x1d4beed4140,
    '0x1d4beffc890': node_0x1d4beffc890,
    '0x1d4beffb860': node_0x1d4beffb860,
    '0x1d4beffc1a0': node_0x1d4beffc1a0,
    '0x1d4beed4e60': node_0x1d4beed4e60,
    '0x1d4c0fe4140': node_0x1d4c0fe4140,
    '0x1d4beffc470': node_0x1d4beffc470,
    '0x1d4c0fba750': node_0x1d4c0fba750,
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

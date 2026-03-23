from __future__ import annotations
import sys
from pathlib import Path
BASE_DIR = Path(r'F:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02')
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from common import as_bool, as_float, as_int, as_text
from Instruments_pythonic import general as general_helpers
def node_0x28b0283c290(context):
    # 布尔常量 (BooleanConstantNode)
    _set_output_value(context, '0x28b0283c290', 'value', True)
    context['last_result'] = True
    return 'flow_out'
def node_0x28b0192d220(context):
    # 阻塞延时循环 (ApiNodeGeneralFlowApiBlockingdelayloop)
    raw_seconds = _read_input_value(context, None, 0.01)
    seconds = as_float(raw_seconds)
    raw_loops = _read_input_value(context, None, 1)
    loops = as_int(raw_loops)
    total_delay = 0.0
    for _ in range(max(0, as_int(loops))):
        general_helpers.delay(max(0.0, as_float(seconds)))
        total_delay += max(0.0, as_float(seconds))
    _set_output_value(context, '0x28b0192d220', 'total_delay', total_delay)
    context['last_result'] = total_delay
    return 'flow_out'
def node_0x28b019cdaf0(context):
    # 开始 (StartNode)
    print('[Start] Demo 02 While 控制流')
    context['last_result'] = 'Demo 02 While 控制流'
    return 'flow_out'
def node_0x28b01aec5c0(context):
    # WHILE 循环 (ApiNodeGeneralFlowApiWhileloop)
    raw_condition = _read_input_value(context, ('0x28b0283c290', 'value'), True)
    condition = as_bool(raw_condition)
    raw_max_iterations = _read_input_value(context, ('0x28b017dfc20', 'value'), 1)
    max_iterations = as_int(raw_max_iterations)
    state = context.setdefault('loop_states', {}).setdefault('0x28b01aec5c0', {'count': 0})
    max_iterations = max(0, as_int(max_iterations))
    if as_bool(condition) and state['count'] < max_iterations:
        state['count'] += 1
        _set_output_value(context, '0x28b01aec5c0', 'iterations', state['count'])
        context['last_result'] = state['count']
        return 'loop_body'
    total_iterations = state.get('count', 0)
    state['count'] = 0
    context['last_result'] = total_iterations
    _set_output_value(context, '0x28b01aec5c0', 'iterations', total_iterations)
    return 'completed'
def node_0x28b017dfc20(context):
    # 最大迭代 (IntegerConstantNode)
    _set_output_value(context, '0x28b017dfc20', 'value', 2)
    context['last_result'] = 2
    return 'flow_out'
def node_0x28b01aee090(context):
    # 返回 (ReturnNode)
    context['return_value'] = context.get('last_result')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
START_NODE_ID = '0x28b019cdaf0'
FLOW_LINKS = {'0x28b0283c290': {'flow_out': '0x28b017dfc20'}, '0x28b0192d220': {'flow_out': '0x28b01aec5c0'}, '0x28b019cdaf0': {'flow_out': '0x28b0283c290'}, '0x28b01aec5c0': {'loop_body': '0x28b0192d220', 'completed': '0x28b01aee090'}, '0x28b017dfc20': {'flow_out': '0x28b01aec5c0'}, '0x28b01aee090': {}}
UNREACHABLE_NODES = []
NODE_NAMES = {
    '0x28b0283c290': '布尔常量',
    '0x28b0192d220': '阻塞延时循环',
    '0x28b019cdaf0': '开始',
    '0x28b01aec5c0': 'WHILE 循环',
    '0x28b017dfc20': '最大迭代',
    '0x28b01aee090': '返回',
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
    '0x28b0283c290': node_0x28b0283c290,
    '0x28b0192d220': node_0x28b0192d220,
    '0x28b019cdaf0': node_0x28b019cdaf0,
    '0x28b01aec5c0': node_0x28b01aec5c0,
    '0x28b017dfc20': node_0x28b017dfc20,
    '0x28b01aee090': node_0x28b01aee090,
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

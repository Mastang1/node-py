from __future__ import annotations
import sys
from pathlib import Path
BASE_DIR = Path(r'F:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_02')
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from common import as_bool, as_float, as_int, as_text
def node_0x1d4beffc1a0(context):
    # 整数常量-左 (IntegerConstantNode)
    _set_output_value(context, '0x1d4beffc1a0', 'value', 1)
    context['last_result'] = 1
    return 'flow_out'
def node_0x1d4beff5970(context):
    # 整数常量-右 (IntegerConstantNode)
    _set_output_value(context, '0x1d4beff5970', 'value', 2)
    context['last_result'] = 2
    return 'flow_out'
def node_0x1d4bebee9f0(context):
    # 数值比较 (CompareNumberNode)
    left_value = as_float(_read_input_value(context, ('0x1d4beffc1a0', 'value'), 0.0))
    right_value = as_float(_read_input_value(context, ('0x1d4beff5970', 'value'), 0.0))
    compare_result = left_value > right_value
    _set_output_value(context, '0x1d4bebee9f0', 'result', compare_result)
    context['last_result'] = compare_result
    return 'flow_out'
def node_0x1d4beffec60(context):
    # 终止-IF (ApiNodeGeneralFlowApiTerminateflow)
    raw_message = _read_input_value(context, None, 'if branch terminated')
    message = as_text(raw_message)
    context['return_value'] = as_text(message, 'Flow terminated')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
def node_0x1d4c0fbb620(context):
    # IF 分支 (ApiNodeGeneralFlowApiIfbranch)
    raw_condition = _read_input_value(context, ('0x1d4beff9730', 'result'), False)
    condition = as_bool(raw_condition)
    raw_true_value = _read_input_value(context, None, 'if_path')
    true_value = as_text(raw_true_value)
    raw_false_value = _read_input_value(context, None, 'fallthrough')
    false_value = as_text(raw_false_value)
    matched = as_bool(condition)
    selected = true_value if matched else false_value
    _set_output_value(context, '0x1d4c0fbb620', 'selected', selected)
    _set_output_value(context, '0x1d4c0fbb620', 'matched', matched)
    context['last_result'] = selected
    return 'true_branch' if matched else 'false_branch'
def node_0x1d4beff9730(context):
    # 布尔逻辑 (BooleanLogicNode)
    left_value = as_bool(_read_input_value(context, ('0x1d4bebee9f0', 'result'), True))
    right_value = as_bool(_read_input_value(context, ('0x1d4beffc1d0', 'result'), True))
    logic_result = left_value or right_value
    _set_output_value(context, '0x1d4beff9730', 'result', logic_result)
    context['last_result'] = logic_result
    return 'flow_out'
def node_0x1d4beffeb70(context):
    # 开始 (StartNode)
    print('[Start] Demo 02 分支控制流')
    context['last_result'] = 'Demo 02 分支控制流'
    return 'flow_out'
def node_0x1d4c0fbaf90(context):
    # ELIF 分支 (ApiNodeGeneralFlowApiElifbranch)
    raw_previous_matched = _read_input_value(context, ('0x1d4c0fbb620', 'matched'), False)
    previous_matched = as_bool(raw_previous_matched)
    raw_condition = _read_input_value(context, ('0x1d4beffc890', 'result'), False)
    condition = as_bool(raw_condition)
    raw_value = _read_input_value(context, None, 'elif_path')
    value = as_text(raw_value)
    matched = (not as_bool(previous_matched)) and as_bool(condition)
    selected = value if matched else ''
    _set_output_value(context, '0x1d4c0fbaf90', 'selected', selected)
    _set_output_value(context, '0x1d4c0fbaf90', 'matched', matched)
    context['last_result'] = selected
    return 'true_branch' if matched else 'false_branch'
def node_0x1d4c0fe58b0(context):
    # 终止-ELIF (ApiNodeGeneralFlowApiTerminateflow)
    raw_message = _read_input_value(context, None, 'elif branch terminated')
    message = as_text(raw_message)
    context['return_value'] = as_text(message, 'Flow terminated')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
def node_0x1d4c0fe5c70(context):
    # 终止-SKIP (ApiNodeGeneralFlowApiTerminateflow)
    raw_message = _read_input_value(context, None, 'else skipped')
    message = as_text(raw_message)
    context['return_value'] = as_text(message, 'Flow terminated')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
def node_0x1d4beed47a0(context):
    # 文本常量-左 (TextConstantNode)
    _set_output_value(context, '0x1d4beed47a0', 'value', 'alpha')
    context['last_result'] = 'alpha'
    return 'flow_out'
def node_0x1d4bec532c0(context):
    # 文本常量-右 (TextConstantNode)
    _set_output_value(context, '0x1d4bec532c0', 'value', 'z')
    context['last_result'] = 'z'
    return 'flow_out'
def node_0x1d4beffc1d0(context):
    # 文本比较 (CompareTextNode)
    left_value = as_text(_read_input_value(context, ('0x1d4beed47a0', 'value'), ''))
    right_value = as_text(_read_input_value(context, ('0x1d4bec532c0', 'value'), ''))
    compare_result = right_value in left_value
    _set_output_value(context, '0x1d4beffc1d0', 'result', compare_result)
    context['last_result'] = compare_result
    return 'flow_out'
def node_0x1d4beffc8f0(context):
    # 布尔常量 (BooleanConstantNode)
    _set_output_value(context, '0x1d4beffc8f0', 'value', True)
    context['last_result'] = True
    return 'flow_out'
def node_0x1d4beffc890(context):
    # 布尔非 (BooleanNotNode)
    bool_value = as_bool(_read_input_value(context, ('0x1d4beffc8f0', 'value'), True))
    not_result = not bool_value
    _set_output_value(context, '0x1d4beffc890', 'result', not_result)
    context['last_result'] = not_result
    return 'flow_out'
def node_0x1d4c0fe41d0(context):
    # ELSE 分支 (ApiNodeGeneralFlowApiElsebranch)
    raw_previous_matched = _read_input_value(context, ('0x1d4c0fbaf90', 'matched'), False)
    previous_matched = as_bool(raw_previous_matched)
    raw_value = _read_input_value(context, None, 'else_path')
    value = as_text(raw_value)
    selected = '' if as_bool(previous_matched) else value
    _set_output_value(context, '0x1d4c0fe41d0', 'selected', selected)
    context['last_result'] = selected
    return 'skipped' if as_bool(previous_matched) else 'else_branch'
def node_0x1d4c0fe5f70(context):
    # 返回 (ReturnNode)
    context['return_value'] = context.get('last_result')
    context['last_result'] = context['return_value']
    context['terminated'] = True
    return None
START_NODE_ID = '0x1d4beffeb70'
FLOW_LINKS = {'0x1d4beffc1a0': {'flow_out': '0x1d4beff5970'}, '0x1d4beff5970': {'flow_out': '0x1d4bebee9f0'}, '0x1d4bebee9f0': {'flow_out': '0x1d4beed47a0'}, '0x1d4beffec60': {}, '0x1d4c0fbb620': {'true_branch': '0x1d4beffec60', 'false_branch': '0x1d4c0fbaf90'}, '0x1d4beff9730': {'flow_out': '0x1d4beffc8f0'}, '0x1d4beffeb70': {'flow_out': '0x1d4beffc1a0'}, '0x1d4c0fbaf90': {'true_branch': '0x1d4c0fe58b0', 'false_branch': '0x1d4c0fe41d0'}, '0x1d4c0fe58b0': {}, '0x1d4c0fe5c70': {}, '0x1d4beed47a0': {'flow_out': '0x1d4bec532c0'}, '0x1d4bec532c0': {'flow_out': '0x1d4beffc1d0'}, '0x1d4beffc1d0': {'flow_out': '0x1d4beff9730'}, '0x1d4beffc8f0': {'flow_out': '0x1d4beffc890'}, '0x1d4beffc890': {'flow_out': '0x1d4c0fbb620'}, '0x1d4c0fe41d0': {'else_branch': '0x1d4c0fe5f70', 'skipped': '0x1d4c0fe5c70'}, '0x1d4c0fe5f70': {}}
UNREACHABLE_NODES = []
NODE_NAMES = {
    '0x1d4beffc1a0': '整数常量-左',
    '0x1d4beff5970': '整数常量-右',
    '0x1d4bebee9f0': '数值比较',
    '0x1d4beffec60': '终止-IF',
    '0x1d4c0fbb620': 'IF 分支',
    '0x1d4beff9730': '布尔逻辑',
    '0x1d4beffeb70': '开始',
    '0x1d4c0fbaf90': 'ELIF 分支',
    '0x1d4c0fe58b0': '终止-ELIF',
    '0x1d4c0fe5c70': '终止-SKIP',
    '0x1d4beed47a0': '文本常量-左',
    '0x1d4bec532c0': '文本常量-右',
    '0x1d4beffc1d0': '文本比较',
    '0x1d4beffc8f0': '布尔常量',
    '0x1d4beffc890': '布尔非',
    '0x1d4c0fe41d0': 'ELSE 分支',
    '0x1d4c0fe5f70': '返回',
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
    '0x1d4beffc1a0': node_0x1d4beffc1a0,
    '0x1d4beff5970': node_0x1d4beff5970,
    '0x1d4bebee9f0': node_0x1d4bebee9f0,
    '0x1d4beffec60': node_0x1d4beffec60,
    '0x1d4c0fbb620': node_0x1d4c0fbb620,
    '0x1d4beff9730': node_0x1d4beff9730,
    '0x1d4beffeb70': node_0x1d4beffeb70,
    '0x1d4c0fbaf90': node_0x1d4c0fbaf90,
    '0x1d4c0fe58b0': node_0x1d4c0fe58b0,
    '0x1d4c0fe5c70': node_0x1d4c0fe5c70,
    '0x1d4beed47a0': node_0x1d4beed47a0,
    '0x1d4bec532c0': node_0x1d4bec532c0,
    '0x1d4beffc1d0': node_0x1d4beffc1d0,
    '0x1d4beffc8f0': node_0x1d4beffc8f0,
    '0x1d4beffc890': node_0x1d4beffc890,
    '0x1d4c0fe41d0': node_0x1d4c0fe41d0,
    '0x1d4c0fe5f70': node_0x1d4c0fe5f70,
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

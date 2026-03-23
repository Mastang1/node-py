from __future__ import annotations

import time
from typing import Any

from ._io import iv_print


def delay(seconds: float) -> None:
    seconds = max(0.0, float(seconds))
    iv_print(f"[General] delay -> {seconds:.3f}s")
    time.sleep(seconds)


def set_variable(variables: dict[str, Any], name: str, value: Any) -> Any:
    variables[str(name)] = value
    iv_print(f"[General] set_variable {name} -> {value!r}")
    return value


def return_value(value: Any) -> Any:
    iv_print(f"[General] return -> {value!r}")
    return value


def raise_error(message: str) -> None:
    iv_print(f"[General] raise_error -> {message}")
    raise RuntimeError(str(message))


def comment(message: str) -> None:
    iv_print(f"[General] comment -> {message}")


class GeneralFlowApi:
    """
    General flow semantics API used to build dynamic API nodes.
    """

    def if_branch(self, condition: bool, true_value: str, false_value: str = "") -> list[Any]:
        """{"func_desc":"If 分支节点：根据 condition 在两个控制流出口之间做选择。","node_name_zh":"IF 分支","node_name_en":"If Branch","category_zh":"通用控制流","category_en":"General Flow","icon":"branch","control_kind":"if_branch","flow_outputs":[{"key":"true_branch","zh":"条件成立"},{"key":"false_branch","zh":"条件不成立"}],"params":[{"name":"condition","zh":"条件","type":"bool","required":true,"default":true,"tooltip":"条件为真时进入 true 分支"},{"name":"true_value","zh":"真分支值","type":"str","required":true,"default":"true_path","tooltip":"条件为真时输出的分支值"},{"name":"false_value","zh":"假分支值","type":"str","required":false,"default":"false_path","tooltip":"条件为假时输出的分支值"}],"returns":[{"name":"selected","zh":"分支结果","type":"str","tooltip":"选择的分支值"},{"name":"matched","zh":"是否命中","type":"bool","tooltip":"是否命中条件"}]}"""
        selected = true_value if bool(condition) else false_value
        iv_print(f"[GeneralFlowApi] if_branch -> selected={selected!r} matched={bool(condition)}")
        return [selected, bool(condition)]

    def elif_branch(self, previous_matched: bool, condition: bool, value: str) -> list[Any]:
        """{"func_desc":"Elif 分支节点：在前置分支未命中时继续判断当前条件。","node_name_zh":"ELIF 分支","node_name_en":"Elif Branch","category_zh":"通用控制流","category_en":"General Flow","icon":"branch","control_kind":"elif_branch","flow_outputs":[{"key":"true_branch","zh":"条件成立"},{"key":"false_branch","zh":"条件不成立"}],"params":[{"name":"previous_matched","zh":"前置命中","type":"bool","required":false,"default":false,"tooltip":"前面分支是否已经命中"},{"name":"condition","zh":"条件","type":"bool","required":true,"default":false,"tooltip":"当前 elif 条件"},{"name":"value","zh":"返回值","type":"str","required":true,"default":"elif_path","tooltip":"命中时输出值"}],"returns":[{"name":"selected","zh":"分支结果","type":"str","tooltip":"命中时返回 value，否则返回空"},{"name":"matched","zh":"是否命中","type":"bool","tooltip":"当前分支是否命中"}]}"""
        matched = (not bool(previous_matched)) and bool(condition)
        selected = value if matched else ""
        iv_print(f"[GeneralFlowApi] elif_branch -> selected={selected!r} matched={matched}")
        return [selected, matched]

    def else_branch(self, previous_matched: bool, value: str) -> list[Any]:
        """{"func_desc":"Else 分支节点：当前置分支都未命中时进入默认出口。","node_name_zh":"ELSE 分支","node_name_en":"Else Branch","category_zh":"通用控制流","category_en":"General Flow","icon":"branch","control_kind":"else_branch","flow_outputs":[{"key":"else_branch","zh":"执行分支"},{"key":"skipped","zh":"跳过"}],"params":[{"name":"previous_matched","zh":"前置命中","type":"bool","required":false,"default":false,"tooltip":"前面分支是否已经命中"},{"name":"value","zh":"返回值","type":"str","required":true,"default":"else_path","tooltip":"else 分支输出值"}],"returns":[{"name":"selected","zh":"分支结果","type":"str","tooltip":"选择的分支值"}]}"""
        selected = "" if bool(previous_matched) else value
        iv_print(f"[GeneralFlowApi] else_branch -> selected={selected!r}")
        return [selected]

    def while_loop(self, condition: bool, max_iterations: int = 10) -> list[Any]:
        """{"func_desc":"While 循环节点：当条件为真时进入循环体，否则从完成出口流出。","node_name_zh":"WHILE 循环","node_name_en":"While Loop","category_zh":"通用控制流","category_en":"General Flow","icon":"loop","control_kind":"while_loop","flow_outputs":[{"key":"loop_body","zh":"循环体"},{"key":"completed","zh":"完成"}],"params":[{"name":"condition","zh":"循环条件","type":"bool","required":true,"default":true,"tooltip":"条件为真时循环"},{"name":"max_iterations","zh":"最大迭代","type":"int","required":false,"default":10,"tooltip":"最大循环次数，避免无限循环"}],"returns":[{"name":"iterations","zh":"当前迭代","type":"int","tooltip":"当前迭代计数"}]}"""
        iterations = 0
        while bool(condition) and iterations < int(max_iterations):
            iterations += 1
            if iterations >= int(max_iterations):
                break
        iv_print(f"[GeneralFlowApi] while_loop -> {iterations}")
        return [iterations]

    def for_range(self, value: int) -> list[Any]:
        """{"func_desc":"For range 节点：按 for i in range(value) 的方式逐次驱动循环体。","node_name_zh":"FOR 循环","node_name_en":"For Range","category_zh":"通用控制流","category_en":"General Flow","icon":"loop","control_kind":"for_range","flow_outputs":[{"key":"loop_body","zh":"循环体"},{"key":"completed","zh":"完成"}],"params":[{"name":"value","zh":"循环次数","type":"int","required":true,"default":5,"tooltip":"for i in range(value) 的 value"}],"returns":[{"name":"current_value","zh":"当前值","type":"int","tooltip":"当前循环值 i"},{"name":"current_index","zh":"当前索引","type":"int","tooltip":"当前循环索引"}]}"""
        items = list(range(int(value)))
        iv_print(f"[GeneralFlowApi] for_range -> {items}")
        return [str(items)]

    def blocking_delay_loop(self, seconds: float, loops: int = 1) -> list[Any]:
        """{"func_desc":"线程阻塞延时循环节点：连续阻塞 loops 次，每次阻塞 seconds。","node_name_zh":"阻塞延时循环","node_name_en":"Blocking Delay Loop","category_zh":"通用控制流","category_en":"General Flow","icon":"loop","control_kind":"blocking_delay_loop","flow_outputs":[{"key":"flow_out","zh":"继续"}],"params":[{"name":"seconds","zh":"单次延时(秒)","type":"float","required":true,"default":0.2,"tooltip":"每轮延时秒数"},{"name":"loops","zh":"循环次数","type":"int","required":false,"default":1,"tooltip":"重复次数"}],"returns":[{"name":"total_delay","zh":"总延时","type":"float","tooltip":"总阻塞时长"}]}"""
        seconds_value = max(0.0, float(seconds))
        loops_value = max(0, int(loops))
        total = 0.0
        for _ in range(loops_value):
            time.sleep(seconds_value)
            total += seconds_value
        iv_print(f"[GeneralFlowApi] blocking_delay_loop -> {total}")
        return [total]

    def terminate_flow(self, message: str = "") -> list[Any]:
        """{"func_desc":"流程终止节点：停止后续控制流并输出终止信息。","node_name_zh":"终止流程","node_name_en":"Terminate Flow","category_zh":"通用控制流","category_en":"General Flow","icon":"stop","control_kind":"terminate_flow","params":[{"name":"message","zh":"终止信息","type":"str","required":false,"default":"Flow terminated","tooltip":"终止时输出的信息"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"终止状态信息"}]}"""
        final_message = message or "Flow terminated"
        iv_print(f"[GeneralFlowApi] terminate_flow -> {final_message}")
        raise RuntimeError(final_message)

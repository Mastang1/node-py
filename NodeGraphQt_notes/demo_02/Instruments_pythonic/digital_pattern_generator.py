from __future__ import annotations

from dataclasses import dataclass, field

from ._io import iv_print


@dataclass
class SimDigitalPatternGeneratorIvi:
    resource_name: str | None = None
    initialized: bool = False
    timing: dict[str, float | str] = field(default_factory=dict)
    loaded_pattern: dict[str, object] = field(default_factory=dict)
    running: bool = False
    handles: dict[str, dict[str, object]] = field(default_factory=dict)
    _handle_counter: int = 0
    last_log: list[str] = field(default_factory=list)

    def _log(self, message: str) -> None:
        self.last_log.append(message)
        iv_print(f"[DigitalPatternGenerator] {message}")

    def _ensure_initialized(self) -> None:
        if not self.initialized:
            raise RuntimeError("Digital pattern generator session is not initialized.")

    def _create_handle(self) -> str:
        self._handle_counter += 1
        return f"dpg_handle_{self._handle_counter}"

    def _resolve_handle(self, handle: str | None) -> str:
        if handle and handle in self.handles:
            return handle
        if self.handles:
            return next(iter(self.handles.keys()))
        raise RuntimeError("No valid digital pattern generator handle was provided.")

    def initialize(self, resource_name: str, id_query: bool = True, reset: bool = False) -> list[object]:
        """{"func_desc":"初始化数字模式发生器并返回句柄与身份。","node_name_zh":"初始化会话","node_name_en":"Initialize Session","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"connect","params":[{"name":"resource_name","zh":"资源名","type":"str","required":true,"default":"PXI0::20-0.0::INSTR","tooltip":"模拟资源地址"},{"name":"id_query","zh":"执行ID查询","type":"bool","required":false,"default":true,"tooltip":"初始化后是否查询身份"},{"name":"reset","zh":"初始化复位","type":"bool","required":false,"default":false,"tooltip":"初始化时是否执行reset"}],"returns":[{"name":"handle","zh":"仪器句柄","type":"handle","tooltip":"后续方法入参使用"},{"name":"identity","zh":"仪器身份","type":"str","tooltip":"设备标识字符串"}]}"""
        self.resource_name = str(resource_name).strip()
        self.initialized = True
        self._log(f"initialize resource={self.resource_name} id_query={id_query} reset={reset}")
        if reset:
            self.reset()
        identity = self.get_identity() if id_query else ""
        handle = self._create_handle()
        self.handles[handle] = {"resource_name": self.resource_name}
        return [handle, identity]

    def get_identity(self) -> str:
        """{"func_desc":"读取数字模式发生器身份信息。","node_name_zh":"查询身份","node_name_en":"Query Identity","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"identity","params":[],"returns":[{"name":"identity","zh":"仪器身份","type":"str","tooltip":"设备标识字符串"}]}"""
        self._ensure_initialized()
        identity = f"SIM-DPG,IVI-PY,RESOURCE={self.resource_name},FW=1.0"
        self._log(f"identity -> {identity}")
        return identity

    def reset(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"复位数字模式发生器状态。","node_name_zh":"复位","node_name_en":"Reset","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"redo","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"复位状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.timing.clear()
        self.loaded_pattern.clear()
        self.running = False
        self._log("reset")
        return ["ok"]

    def self_test(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"执行数字模式发生器自检。","node_name_zh":"自检","node_name_en":"Self Test","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"test","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"code","zh":"结果码","type":"int","tooltip":"0表示通过"},{"name":"message","zh":"结果信息","type":"str","tooltip":"自检详情"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        result = [0, "Digital pattern generator self test passed"]
        self._log(f"self_test -> {result}")
        return result

    def configure_timing(self, sample_rate: float, logic_level: str = "3.3V", handle: str | None = None) -> list[object]:
        """{"func_desc":"配置数字输出时序。","node_name_zh":"配置时序","node_name_en":"Configure Timing","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"timing","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"sample_rate","zh":"采样率(Hz)","type":"float","required":true,"default":1000000.0,"tooltip":"数字采样率"},{"name":"logic_level","zh":"逻辑电平","type":"enum","required":false,"default":"3.3V","options":["1.8V","2.5V","3.3V","5V"],"tooltip":"逻辑电平"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"配置状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.timing = {
            "sample_rate": float(sample_rate),
            "logic_level": str(logic_level),
        }
        self._log(f"configure_timing -> {self.timing}")
        return ["ok"]

    def load_pattern(self, pattern_name: str, pattern_bits: str, loop_count: int = 1, handle: str | None = None) -> list[object]:
        """{"func_desc":"加载数字模式数据。","node_name_zh":"加载模式","node_name_en":"Load Pattern","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"pattern_load","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"pattern_name","zh":"模式名","type":"str","required":true,"default":"burst_A","tooltip":"模式名称"},{"name":"pattern_bits","zh":"模式比特","type":"str","required":true,"default":"101100111000","tooltip":"比特串"},{"name":"loop_count","zh":"循环次数","type":"int","required":false,"default":1,"tooltip":"模式循环次数"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"加载状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.loaded_pattern = {
            "pattern_name": str(pattern_name),
            "pattern_bits": str(pattern_bits),
            "loop_count": int(loop_count),
        }
        self._log(f"load_pattern -> {self.loaded_pattern}")
        return ["ok"]

    def start_output(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"启动数字模式输出。","node_name_zh":"开始输出","node_name_en":"Start Output","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"run","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"输出状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.running = True
        self._log("start_output")
        return ["running"]

    def stop_output(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"停止数字模式输出。","node_name_zh":"停止输出","node_name_en":"Stop Output","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"stop","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"输出状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.running = False
        self._log("stop_output")
        return ["stopped"]

    def query_status(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"查询输出状态。","node_name_zh":"查询状态","node_name_en":"Query Status","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"validate","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"running","zh":"运行状态","type":"bool","tooltip":"是否正在输出"},{"name":"timing","zh":"时序配置","type":"str","tooltip":"时序摘要"},{"name":"pattern_loaded","zh":"已加载模式","type":"bool","tooltip":"是否已加载模式"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        status = {
            "running": self.running,
            "timing": self.timing.copy(),
            "pattern_loaded": bool(self.loaded_pattern),
        }
        self._log(f"query_status -> {status}")
        return [status["running"], str(status["timing"]), status["pattern_loaded"]]

    def close(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"关闭会话。","node_name_zh":"关闭会话","node_name_en":"Close Session","category_zh":"数字模式发生器","category_en":"Digital Pattern Generator","icon":"stop","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则关闭最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"关闭状态"}]}"""
        if not self.initialized:
            self._log("close skipped - session not initialized")
            return ["skipped"]
        if handle:
            self.handles.pop(handle, None)
        elif self.handles:
            self.handles.pop(next(iter(self.handles.keys())), None)
        self._log(f"close resource={self.resource_name}")
        self.initialized = bool(self.handles)
        if not self.initialized:
            self.resource_name = None
        self.running = False
        return ["ok"]

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimSignalGeneratorIvi:
    resource_name: str | None = None
    initialized: bool = False
    output_states: dict[str, bool] = field(default_factory=dict)
    channel_settings: dict[str, dict[str, float | str]] = field(default_factory=dict)
    handles: dict[str, dict[str, object]] = field(default_factory=dict)
    _handle_counter: int = 0
    last_log: list[str] = field(default_factory=list)

    def _log(self, message: str) -> None:
        self.last_log.append(message)
        print(f"[SignalGenerator] {message}")

    def _ensure_initialized(self) -> None:
        if not self.initialized:
            raise RuntimeError("Signal generator session is not initialized.")

    def _create_handle(self) -> str:
        self._handle_counter += 1
        return f"sg_handle_{self._handle_counter}"

    def _resolve_handle(self, handle: str | None) -> str:
        if handle and handle in self.handles:
            return handle
        if self.handles:
            return next(iter(self.handles.keys()))
        raise RuntimeError("No valid signal generator handle was provided.")

    def initialize(self, resource_name: str, id_query: bool = True, reset: bool = False) -> list[object]:
        """{"func_desc":"初始化信号发生器并返回仪器句柄与身份字符串。","node_name_zh":"初始化会话","node_name_en":"Initialize Session","category_zh":"信号发生器","category_en":"Signal Generator","icon":"connect","params":[{"name":"resource_name","zh":"资源名","type":"str","required":true,"default":"TCPIP0::192.168.0.10::INSTR","tooltip":"模拟资源地址"},{"name":"id_query","zh":"执行ID查询","type":"bool","required":false,"default":true,"tooltip":"初始化后是否查询身份"},{"name":"reset","zh":"初始化复位","type":"bool","required":false,"default":false,"tooltip":"初始化时是否执行reset"}],"returns":[{"name":"handle","zh":"仪器句柄","type":"handle","tooltip":"后续方法入参使用"},{"name":"identity","zh":"仪器身份","type":"str","tooltip":"设备标识字符串"}]}"""
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
        """{"func_desc":"读取信号发生器身份信息。","node_name_zh":"查询身份","node_name_en":"Query Identity","category_zh":"信号发生器","category_en":"Signal Generator","icon":"identity","params":[],"returns":[{"name":"identity","zh":"仪器身份","type":"str","tooltip":"设备标识字符串"}]}"""
        self._ensure_initialized()
        identity = f"SIM-SG,IVI-PY,RESOURCE={self.resource_name},FW=1.0"
        self._log(f"identity -> {identity}")
        return identity

    def reset(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"复位信号发生器状态。","node_name_zh":"复位","node_name_en":"Reset","category_zh":"信号发生器","category_en":"Signal Generator","icon":"redo","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"复位状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.output_states.clear()
        self.channel_settings.clear()
        self._log("reset")
        return ["ok"]

    def self_test(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"执行自检。","node_name_zh":"自检","node_name_en":"Self Test","category_zh":"信号发生器","category_en":"Signal Generator","icon":"test","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"code","zh":"结果码","type":"int","tooltip":"0表示通过"},{"name":"message","zh":"结果信息","type":"str","tooltip":"自检详情"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        result = [0, "Signal generator self test passed"]
        self._log(f"self_test -> {result}")
        return result

    def configure_waveform(
        self,
        channel: str,
        waveform: str,
        frequency: float,
        amplitude: float,
        offset: float = 0.0,
        phase: float = 0.0,
        handle: str | None = None,
    ) -> list[object]:
        """{"func_desc":"配置输出波形参数。","node_name_zh":"配置波形","node_name_en":"Configure Waveform","category_zh":"信号发生器","category_en":"Signal Generator","icon":"waveform","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"channel","zh":"通道","type":"enum","required":true,"default":"CH1","options":["CH1","CH2","CH3","CH4"],"tooltip":"输出通道"},{"name":"waveform","zh":"波形","type":"enum","required":true,"default":"SINE","options":["SINE","SQUARE","TRIANGLE","PULSE"],"tooltip":"波形类型"},{"name":"frequency","zh":"频率(Hz)","type":"float","required":true,"default":1000.0,"tooltip":"输出频率"},{"name":"amplitude","zh":"幅值(Vpp)","type":"float","required":true,"default":1.0,"tooltip":"输出幅值"},{"name":"offset","zh":"偏置(V)","type":"float","required":false,"default":0.0,"tooltip":"直流偏置"},{"name":"phase","zh":"相位(度)","type":"float","required":false,"default":0.0,"tooltip":"输出相位"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"配置状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        channel_name = str(channel).upper()
        self.channel_settings[channel_name] = {
            "waveform": str(waveform).upper(),
            "frequency": float(frequency),
            "amplitude": float(amplitude),
            "offset": float(offset),
            "phase": float(phase),
        }
        self._log(f"configure_waveform {channel_name} -> {self.channel_settings[channel_name]}")
        return ["ok"]

    def configure_output(self, channel: str, enabled: bool, handle: str | None = None) -> list[object]:
        """{"func_desc":"设置指定通道输出开关。","node_name_zh":"输出开关","node_name_en":"Output Enable","category_zh":"信号发生器","category_en":"Signal Generator","icon":"power","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"channel","zh":"通道","type":"enum","required":true,"default":"CH1","options":["CH1","CH2","CH3","CH4"],"tooltip":"输出通道"},{"name":"enabled","zh":"使能","type":"bool","required":true,"default":true,"tooltip":"是否使能输出"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"输出设置状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        channel_name = str(channel).upper()
        self.output_states[channel_name] = bool(enabled)
        self._log(f"configure_output {channel_name} -> {self.output_states[channel_name]}")
        return ["ok"]

    def close(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"关闭会话。","node_name_zh":"关闭会话","node_name_en":"Close Session","category_zh":"信号发生器","category_en":"Signal Generator","icon":"stop","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则关闭最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"关闭状态"}]}"""
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
        return ["ok"]

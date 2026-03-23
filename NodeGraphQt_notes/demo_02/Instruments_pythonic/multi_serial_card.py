from __future__ import annotations

from dataclasses import dataclass, field

from ._io import iv_print


@dataclass
class SimMultiSerialCardIvi:
    resource_name: str | None = None
    initialized: bool = False
    ports: dict[str, dict[str, object]] = field(default_factory=dict)
    handles: dict[str, dict[str, object]] = field(default_factory=dict)
    _handle_counter: int = 0
    last_log: list[str] = field(default_factory=list)

    def _log(self, message: str) -> None:
        self.last_log.append(message)
        iv_print(f"[MultiSerialCard] {message}")

    def _ensure_initialized(self) -> None:
        if not self.initialized:
            raise RuntimeError("Multi serial card session is not initialized.")

    def _create_handle(self) -> str:
        self._handle_counter += 1
        return f"serial_handle_{self._handle_counter}"

    def _resolve_handle(self, handle: str | None) -> str:
        if handle and handle in self.handles:
            return handle
        if self.handles:
            return next(iter(self.handles.keys()))
        raise RuntimeError("No valid multi serial card handle was provided.")

    def _ensure_port_open(self, channel: str) -> dict[str, object]:
        channel_name = str(channel).upper()
        port_state = self.ports.get(channel_name)
        if not port_state or not port_state.get("opened"):
            raise RuntimeError(f"Serial port for channel {channel_name} is not open.")
        return port_state

    def initialize(self, resource_name: str, id_query: bool = True, reset: bool = False) -> list[object]:
        """{"func_desc":"初始化多通道串口卡并返回句柄与身份。","node_name_zh":"初始化会话","node_name_en":"Initialize Session","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"connect","params":[{"name":"resource_name","zh":"资源名","type":"str","required":true,"default":"PCI::SERIAL-CARD-01","tooltip":"模拟资源地址"},{"name":"id_query","zh":"执行ID查询","type":"bool","required":false,"default":true,"tooltip":"初始化后是否查询身份"},{"name":"reset","zh":"初始化复位","type":"bool","required":false,"default":false,"tooltip":"初始化时是否执行reset"}],"returns":[{"name":"handle","zh":"仪器句柄","type":"handle","tooltip":"后续方法入参使用"},{"name":"identity","zh":"仪器身份","type":"str","tooltip":"设备标识字符串"}]}"""
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
        """{"func_desc":"读取串口卡身份信息。","node_name_zh":"查询身份","node_name_en":"Query Identity","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"identity","params":[],"returns":[{"name":"identity","zh":"仪器身份","type":"str","tooltip":"设备标识字符串"}]}"""
        self._ensure_initialized()
        identity = f"SIM-MSC,IVI-PY,RESOURCE={self.resource_name},FW=1.0"
        self._log(f"identity -> {identity}")
        return identity

    def reset(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"复位串口卡状态。","node_name_zh":"复位","node_name_en":"Reset","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"redo","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"复位状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        self.ports.clear()
        self._log("reset")
        return ["ok"]

    def self_test(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"执行串口卡自检。","node_name_zh":"自检","node_name_en":"Self Test","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"test","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"}],"returns":[{"name":"code","zh":"结果码","type":"int","tooltip":"0表示通过"},{"name":"message","zh":"结果信息","type":"str","tooltip":"自检详情"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        result = [0, "Multi serial card self test passed"]
        self._log(f"self_test -> {result}")
        return result

    def open_port(
        self,
        channel: str,
        port_name: str,
        baud_rate: int,
        data_bits: int = 8,
        parity: str = "N",
        stop_bits: int = 1,
        timeout: float = 1.0,
        handle: str | None = None,
    ) -> list[object]:
        """{"func_desc":"打开指定通道串口。","node_name_zh":"打开端口","node_name_en":"Open Port","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"port","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"channel","zh":"通道","type":"enum","required":true,"default":"CH1","options":["CH1","CH2","CH3","CH4"],"tooltip":"逻辑通道"},{"name":"port_name","zh":"端口名","type":"str","required":true,"default":"COM1","tooltip":"系统串口名"},{"name":"baud_rate","zh":"波特率","type":"int","required":true,"default":115200,"tooltip":"通信波特率"},{"name":"data_bits","zh":"数据位","type":"int","required":false,"default":8,"tooltip":"数据位"},{"name":"parity","zh":"校验位","type":"enum","required":false,"default":"N","options":["N","E","O"],"tooltip":"串口校验位"},{"name":"stop_bits","zh":"停止位","type":"int","required":false,"default":1,"tooltip":"停止位"},{"name":"timeout","zh":"超时(秒)","type":"float","required":false,"default":1.0,"tooltip":"通信超时"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"打开状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        channel_name = str(channel).upper()
        self.ports[channel_name] = {
            "opened": True,
            "port_name": str(port_name),
            "baud_rate": int(baud_rate),
            "data_bits": int(data_bits),
            "parity": str(parity).upper(),
            "stop_bits": int(stop_bits),
            "timeout": float(timeout),
            "last_write": "",
            "rx_buffer": f"SIM-REPLY:{channel_name}:{port_name}",
        }
        self._log(f"open_port {channel_name} -> {self.ports[channel_name]}")
        return ["ok"]

    def write(self, channel: str, data: str, encoding: str = "utf-8", handle: str | None = None) -> list[object]:
        """{"func_desc":"向串口写入数据。","node_name_zh":"写串口","node_name_en":"Write","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"write","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"channel","zh":"通道","type":"enum","required":true,"default":"CH1","options":["CH1","CH2","CH3","CH4"],"tooltip":"逻辑通道"},{"name":"data","zh":"写入数据","type":"str","required":true,"default":"*IDN?","tooltip":"待写入文本"},{"name":"encoding","zh":"编码","type":"str","required":false,"default":"utf-8","tooltip":"字符编码"}],"returns":[{"name":"bytes_written","zh":"写入字节数","type":"int","tooltip":"写入总字节数"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        port_state = self._ensure_port_open(channel)
        payload = str(data).encode(encoding)
        port_state["last_write"] = str(data)
        port_state["rx_buffer"] = f"ECHO:{data}"
        self._log(f"write {str(channel).upper()} bytes={len(payload)} data={data!r}")
        return [len(payload)]

    def read(self, channel: str, size: int = 0, timeout: float | None = None, handle: str | None = None) -> list[object]:
        """{"func_desc":"从串口读取数据。","node_name_zh":"读串口","node_name_en":"Read","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"read","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"channel","zh":"通道","type":"enum","required":true,"default":"CH1","options":["CH1","CH2","CH3","CH4"],"tooltip":"逻辑通道"},{"name":"size","zh":"读取长度","type":"int","required":false,"default":0,"tooltip":"0表示读取全部"},{"name":"timeout","zh":"超时(秒)","type":"float","required":false,"default":1.0,"tooltip":"读取超时"}],"returns":[{"name":"reply","zh":"返回数据","type":"str","tooltip":"读取的响应文本"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        port_state = self._ensure_port_open(channel)
        payload = str(port_state.get("rx_buffer", ""))
        if size and size > 0:
            payload = payload[: int(size)]
        self._log(f"read {str(channel).upper()} timeout={timeout} -> {payload!r}")
        return [payload]

    def close_port(self, channel: str, handle: str | None = None) -> list[object]:
        """{"func_desc":"关闭指定通道串口。","node_name_zh":"关闭端口","node_name_en":"Close Port","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"port","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则使用最近句柄"},{"name":"channel","zh":"通道","type":"enum","required":true,"default":"CH1","options":["CH1","CH2","CH3","CH4"],"tooltip":"逻辑通道"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"关闭状态"}]}"""
        self._ensure_initialized()
        _ = self._resolve_handle(handle)
        channel_name = str(channel).upper()
        if channel_name not in self.ports:
            self._log(f"close_port skipped - {channel_name} not opened")
            return ["skipped"]
        self.ports[channel_name]["opened"] = False
        self._log(f"close_port {channel_name}")
        return ["ok"]

    def close(self, handle: str | None = None) -> list[object]:
        """{"func_desc":"关闭串口卡会话。","node_name_zh":"关闭会话","node_name_en":"Close Session","category_zh":"多通道串口卡","category_en":"Multi Serial Card","icon":"stop","params":[{"name":"handle","zh":"仪器句柄","type":"handle","required":false,"default":"","tooltip":"可选，未提供则关闭最近句柄"}],"returns":[{"name":"status","zh":"状态","type":"str","tooltip":"关闭状态"}]}"""
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

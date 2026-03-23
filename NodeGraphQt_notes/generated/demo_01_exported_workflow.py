from __future__ import annotations

import time

class VirtualInstrumentAPI:
    def __init__(self):
        self.resource_name = None
        self.is_open = False
        self.channels = {
            "CH1": {"enabled": False, "voltage": 0.0},
            "CH2": {"enabled": False, "voltage": 0.0},
        }

    def _ensure_open(self):
        if not self.is_open:
            raise RuntimeError("Instrument session is not open.")

    def _get_channel(self, channel):
        channel_name = str(channel).strip().upper()
        if channel_name not in self.channels:
            raise RuntimeError(f"Unknown channel: {channel_name}")
        return channel_name, self.channels[channel_name]

    def open(self, resource_name):
        self.resource_name = str(resource_name).strip()
        self.is_open = True
        print(f"[API] open -> {self.resource_name}")

    def enable_output(self, channel, enabled):
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        state["enabled"] = bool(enabled)
        print(f"[API] output {channel_name} -> {state['enabled']}")

    def set_voltage(self, channel, voltage):
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        state["voltage"] = float(voltage)
        print(f"[API] set voltage {channel_name} -> {state['voltage']:.3f} V")

    def measure_voltage(self, channel):
        self._ensure_open()
        channel_name, state = self._get_channel(channel)
        value = round(state["voltage"] + (0.002 if state["enabled"] else 0.0), 4)
        print(f"[API] measure {channel_name} -> {value:.4f} V")
        return value

    def close(self):
        if not self.is_open:
            print("[API] close skipped - already closed")
            return
        print(f"[API] close -> {self.resource_name}")
        self.is_open = False
        self.resource_name = None


def main():
    context = {}
    api = None
    print('[Exported Workflow] start')

    # Start (StartNode)
    print('[Start] test')

    # Open PSU (OpenInstrumentNode)
    api = VirtualInstrumentAPI()
    context['api'] = api
    api.open('TCPIP0::192.168.0.8::INSTR')

    # Enable CH1 (SetOutputNode)
    if api is None or not api.is_open:
        raise RuntimeError('Enable CH1 requires an open instrument session. Add Open Instrument before this node.')
    api.enable_output('CH1', True)

    # Set CH1 Voltage (SetVoltageNode)
    if api is None or not api.is_open:
        raise RuntimeError('Set CH1 Voltage requires an open instrument session. Add Open Instrument before this node.')
    api.set_voltage('CH1', 5.0)

    # Settle (DelayNode)
    print('[Delay] 0.100 s')
    time.sleep(0.1)

    # Measure CH1 (MeasureVoltageNode)
    if api is None or not api.is_open:
        raise RuntimeError('Measure CH1 requires an open instrument session. Add Open Instrument before this node.')
    context['measured_voltage'] = api.measure_voltage('CH1')
    print('[Store] measured_voltage =', context['measured_voltage'])

    # Print Result (PrintContextNode)
    print('Measured voltage:', context.get('measured_voltage', '<missing>'))

    # Close PSU (CloseInstrumentNode)
    if api is not None and api.is_open:
        api.close()
    else:
        print('[Close] skipped - no open session')

    if api is not None and api.is_open:
        api.close()
    print('[Exported Workflow] done')


if __name__ == '__main__':
    main()

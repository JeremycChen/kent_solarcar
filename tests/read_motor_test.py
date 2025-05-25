import can
import struct

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_ID = 0x64           # your “CAN TX address”
CHANNEL = 0 # python-can channel name
BITRATE = 250000         # bus bit rate in bit/s

# ─── PARSERS ──────────────────────────────────────────────────────────────────

def parse_status_0(data):
    cv = struct.unpack_from('<h', data, 0)[0]
    b3 = data[2]
    ctrl_mode  = (b3 >> 1) & 0x01
    motor_mode = (b3 >> 3) & 0x07
    sw_en      = bool((b3 >> 6) & 0x01)
    m_state    = (b3 >> 7) & 0x03
    torque     = struct.unpack_from('<h', data, 3)[0]
    rpm_raw    = struct.unpack_from('<h', data, 5)[0]
    temp       = struct.unpack_from('<b', data, 7)[0]
    return {
        'control_value': cv,
        'control_mode':  ctrl_mode,
        'motor_mode':    motor_mode,
        'sw_enable':     sw_en,
        'motor_state':   m_state,
        'motor_torque':  torque,
        'motor_rpm':     rpm_raw * 0.1,
        'motor_temp':    temp,
    }

def parse_status_1(data):
    pk = struct.unpack_from('<h', data, 0)[0]
    pw = struct.unpack_from('<h', data, 2)[0]
    pos_raw = struct.unpack_from('<H', data, 4)[0]
    return {
        'inv_peak_current_A': pk,
        'motor_power_W':      pw,
        'abs_position_deg':   pos_raw * 0.1,
    }

def bits_set(u64):
    return [i for i in range(64) if (u64 >> i) & 1]

def parse_status_2(data):
    code = struct.unpack_from('<Q', data, 0)[0]
    return {'warning_bits_set': bits_set(code)}

def parse_status_3(data):
    code = struct.unpack_from('<Q', data, 0)[0]
    return {'error_bits_set': bits_set(code)}

# ─── MAIN ─────────────────────────────────────────────────────────────────────

parsers = {
    BASE_ID + 0: (parse_status_0, 'status_0'),
    BASE_ID + 1: (parse_status_1, 'status_1'),
    BASE_ID + 2: (parse_status_2, 'status_2'),
    BASE_ID + 3: (parse_status_3, 'status_3'),
}

bus = can.Bus(interface='gs_usb', channel=CHANNEL, bitrate=BITRATE, state=can.BusState.PASSIVE)
print(f"Listening on {CHANNEL} @ {BITRATE} bit/s for IDs {list(map(hex, parsers))}")

try:
    for msg in bus:
        parser = parsers.get(msg.arbitration_id)
        if parser and len(msg.data) >= 1:
            fn, name = parser
            decoded = fn(msg.data)
            print(f"{name} (0x{msg.arbitration_id:X}): {decoded}")
except KeyboardInterrupt:
    pass
finally:
    bus.shutdown()

import serial
import time

PORT = 'COM9' 
BAUD  = 9600

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)  # let the Arduino reboot

def set_relay(on: bool, timeout: float = 1.0) -> bool:
    """
    Turn the relay on or off.
    Returns True if we saw ACK,RELAY,1 (or 0), raises on ERR or timeout.
    """
    # 1) clear any pending DATA… lines
    ser.reset_input_buffer()

    # 2) send the command
    cmd = '1\n' if on else '0\n'
    ser.write(cmd.encode())

    # 3) wait for the right response
    deadline = time.time() + timeout
    while time.time() < deadline:
        raw = ser.readline().decode().strip()
        if not raw:
            continue

        parts = raw.split(',')
        tag = parts[0]

        # successful ack
        if tag == 'ACK' and parts[1] == 'RELAY':
            return (parts[2] == ('1' if on else '0'))

        # error from relay handler
        if tag == 'ERR' and parts[1] == 'RELAY':
            raise RuntimeError(f"Relay error: {parts[2]}")

        # otherwise: drop this line (PROTO: maybe DATA,SENSOR,…)
        # and keep waiting

    raise TimeoutError("No ACK,RELAY in time")

def read_sensor(timeout: float=2.0):
    """
    Reads the next DATA,SENSOR line; skips ERR/SENSOR or anything else.
    """
    end = time.time() + timeout
    while time.time() < end:
        line = ser.readline().decode().strip()
        if not line: 
            continue
        parts = line.split(',')
        if parts[0] == 'DATA' and parts[1] == 'SENSOR' and len(parts)==5:
            return {
                'temp_c': float(parts[2]),
                'temp_f': float(parts[3]),
                'humidity': float(parts[4]),
            }
        if parts[0] == 'ERR' and parts[1] == 'SENSOR':
            raise RuntimeError("Sensor read failed")
        # else ignore
    raise TimeoutError("No sensor data in time")

if __name__ == '__main__':
    try:
        print("Relay ON →", set_relay(True))
        time.sleep(5)
        print("Relay OFF →", set_relay(False))

        while True:
            d = read_sensor()
            print(f"{d['temp_c']:.2f}°C  {d['temp_f']:.2f}°F  Humidity: {d['humidity']:.2f}%")
    finally:
        ser.close()

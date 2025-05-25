import serial
import time
import os
import glob
import threading
import concurrent.futures

# Configuration
PORT                = 'COM9'
BAUD                = 9600
FOLDER              = r"C:\Users\LattePanda\Downloads\BMSTool-V1.14.231\BMSTool-V1.14.23\SaveData"
INACTIVITY_TIMEOUT  = 3    # seconds
CUT_OFF_THRESHOLD   = 12.5  # your cut-off
CONNECTION_THRESHOLD = 13.4

# Global serial handle + lock + relay state
ser         = None
ser_lock    = threading.Lock()
relay_state = False  # False == OFF, True == ON

def set_relay(on: bool, timeout: float = 1.0) -> bool:
    """Atomically send relay command and wait for ACK."""
    with ser_lock:
        ser.reset_input_buffer()
        cmd = '1\n' if on else '0\n'
        ser.write(cmd.encode())
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = ser.readline().decode().strip()
            if not raw:
                continue
            parts = raw.split(',')
            if parts[0]=='ACK' and parts[1]=='RELAY':
                return (parts[2]==('1' if on else '0'))
            if parts[0]=='ERR' and parts[1]=='RELAY':
                raise RuntimeError(f"Relay error: {parts[2]}")
        raise TimeoutError("No ACK,RELAY in time")

def read_sensor(timeout: float = 2.0):
    """Atomically grab the next sensor DATA,SENSOR line."""
    with ser_lock:
        end = time.time() + timeout
        while time.time() < end:
            raw = ser.readline().decode().strip()
            if not raw:
                continue
            parts = raw.split(',')
            if parts[0]=='DATA' and parts[1]=='SENSOR' and len(parts)==5:
                return {
                    'temp_c':   float(parts[2]),
                    'temp_f':   float(parts[3]),
                    'humidity': float(parts[4])
                }
            if parts[0]=='ERR' and parts[1]=='SENSOR':
                raise RuntimeError("Sensor read failed")
        raise TimeoutError("No sensor data in time")

def read_and_print_sensor():
    try:
        d = read_sensor()
        print(f"{d['temp_c']:.2f}°C  {d['temp_f']:.2f}°F  Humidity: {d['humidity']:.2f}%")
    except Exception as e:
        print("Sensor read error:", e)

def get_latest_csv(folder: str) -> str:
    csvs = glob.glob(os.path.join(folder, "*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {folder!r}")
    return max(csvs, key=os.path.getmtime)

def tail_csv(folder: str, sleep_secs: float = 0.2):
    """Yield every new line, from the end of the latest CSV."""
    path = get_latest_csv(folder)
    with open(path, 'r', newline='') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(sleep_secs)
                continue
            yield line.rstrip('\r\n')

if __name__ == '__main__':
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(2)  # device reboot

    # start with relay ON
    relay_state = True
    print("Relay ON →", set_relay(True))

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    last_row_time = time.time()
    stop_event = threading.Event()
        # heartbeat: resend current relay state every KEEPALIVE_INTERVAL
    def heartbeat(interval):
        global relay_state
        while True:
            time.sleep(interval)
            with ser_lock:
                # simply re-send “1\n” or “0\n” as a keepalive
                msg = '1\n' if relay_state else '0\n'
                ser.write(msg.encode())

    # start heartbeat at half the Arduino timeout
    KEEPALIVE_INTERVAL = INACTIVITY_TIMEOUT / 2
    threading.Thread(
        target=heartbeat,
        args=(KEEPALIVE_INTERVAL,),
        daemon=True
    ).start()
    
    def inactivity_watchdog(timeout):
        global relay_state
        while not stop_event.is_set():
            time.sleep(1)
            if time.time() - last_row_time > timeout and relay_state:
                print(f"No CSV for {timeout}s → Relay OFF")
                try:
                    set_relay(False)
                except Exception as e:
                    print("Failed to turn off relay on inactivity:", e)
                relay_state = False

    threading.Thread(
        target=inactivity_watchdog,
        args=(INACTIVITY_TIMEOUT,),
        daemon=True
    ).start()

    try:
        for row in tail_csv(FOLDER):
            last_row_time = time.time()
            data = row.split(',')
            print("New row:", data)

            # fire off sensor read in background
            executor.submit(read_and_print_sensor)

            # threshold logic — NO outer ser_lock
            try:
                value = float(data[3])
            except (IndexError, ValueError):
                continue

            if value < CUT_OFF_THRESHOLD and relay_state:
                print("Value below threshold → Relay OFF →", set_relay(False))
                relay_state = False
            elif value >= CONNECTION_THRESHOLD and not relay_state:
                print("Value back above threshold → Relay ON →", set_relay(True))
                relay_state = True

    except KeyboardInterrupt:
        print("\nInterrupted by user, shutting down.")
    finally:
        stop_event.set()
        executor.shutdown(wait=False)
        ser.close()

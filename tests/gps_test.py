from serial import Serial
from pynmeagps import NMEAReader
with Serial('COM7', 115200, timeout=3) as stream:
  while True:
    nmr = NMEAReader(stream)
    raw_data, parsed_data = nmr.read()
    if parsed_data is not None:
        try:
            print(parsed_data)
            print("lat: " + str(parsed_data.lat))
            print("long: " + str(parsed_data.long))
            print("spd: " + str(parsed_data.spd))
        except Exception as e:
            print(f"No gps data: {e}")

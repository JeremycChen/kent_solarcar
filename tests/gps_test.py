from serial import Serial
from pynmeagps import NMEAReader
with Serial('COM7', 115200, timeout=3) as stream:
  while True:
    nmr = NMEAReader(stream)
    raw_data, parsed_data = nmr.read()
    if parsed_data is not None:
        print(parsed_data)
        print("lat: " + parsed_data.lat)
        print("long: " + parsed_data.long)
        print("spd: " +parsed_data.spd)
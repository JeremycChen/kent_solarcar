from serial import Serial
from pynmeagps import NMEAReader
with Serial('COM7', 115200, timeout=3) as stream:
  while True:
    nmr = NMEAReader(stream)
    raw_data, parsed_data = nmr.read()
    if parsed_data is not None:
        print(parsed_data)
        print(parsed_data.lat)
        print(parsed_data.long)
        print(parsed_data.spd)
from serial import Serial
from pynmeagps import NMEAReader

with Serial('COM3', 115200, timeout=3) as stream:
    try:
        nmr = NMEAReader(stream)
        while True:
            raw_data, parsed_data = nmr.read()
            if parsed_data is not None:
                try:
                    print(parsed_data)
                    if hasattr(parsed_data, 'lat') and hasattr(parsed_data, 'long') and hasattr(parsed_data, 'spd'):
                        print("lat: " + str(parsed_data.lat))
                        print("long: " + str(parsed_data.long))
                        print("spd: " + str(parsed_data.spd))
                    else:
                        print("Parsed data does not contain lat, long, or spd attributes.")
                except Exception as e:
                    print(f"No gps data: {e}")
    finally:
        stream.close()
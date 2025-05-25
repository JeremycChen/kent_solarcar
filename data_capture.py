# data_capture.py
import serial
import time
import re

# from telemetrix import telemetrix
from pynmeagps import NMEAReader


#physical constants
WHEEL_DIAMETER = 2.153412 #meters

# Touch sensor pin#
ENCODER_PIN = 7  # arduino pin number

#dht sensor pin#
DHT_PIN = 4

# Battery Sensor pin#
BATTERY_VOLTMETER_PIN = 5

# Telemetrix Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

# GPS counter range ((x0,y0),(x1,y1))
GPS_BOUNDS = ((33.03467, -97.28418), (33.03450, -97.28480)) #((33.03467, -97.28418), (33.03458, -97.28470))

class DataCapture:
    def __init__(self):
        self.start_time = time.time()
        self.gps_prev_t = time.time()

        self.encoder = False
        self.prev_encoder = False
        self.rotation = 0

        #data that will be displayed
        self.data = {
            "speed": 0.0,
            "distance": 0.0,
            "temperature": 0,
            "time": 0.0,
            "battery": 0,
            "battery_I": 0,
            "lap": 0,
            'V': 0,
            'I': 0,
            "I_1": 0,
            "I_2": 0,
            "PPV_1": 0,
            "PPV_2": 0,
            'PPV': 0,
            "gps": [0,0],
            "gps_bounds": GPS_BOUNDS
        }

        self.prev_data = self.data

        # self.board = None
        self.solar_panel_1_serial = None
        self.solar_panel_2_serial = None
        self.gps_serial = None
        self.gps_reader = None
        self.battery_serial = None

        # self.board_setup()
        # self.dht_setup(self.board, DHT_PIN, self.dht_callback, 11)
        # self.speed_encoder_setup(self.board, ENCODER_PIN)    
        # self.battery_voltmeter_setup(self.board, BATTERY_VOLTMETER_PIN)

        self.connection_status = {
            'solar1':    {'ok': False, 'err': None},
            'solar2':    {'ok': False, 'err': None},
            'gps':       {'ok': False, 'err': None},
            'battery':   {'ok': False, 'err': None},
        }

        self.solar_panel_serial_setup()
        self.gps_setup()
        self.battery_serial_setup()


    def battery_serial_setup(self):
        try:
            self.battery_serial = serial.Serial('COM3', 19200, timeout=0)
            self.connection_status['battery']['ok'] = True
        except Exception as e:
            self.battery_serial = None
            self.connection_status['battery'].update(ok=False, err=str(e))

    def get_data(self):
        self.update_data()
        return self.data

    def update_data(self):
        #order matters
        self.update_time()
        # self.update_speed()
        self.update_solar_panel()
        self.update_gps()
        self.update_distance()

        self.update_battery()
    
    def update_time(self):
        t = time.time() - self.start_time
        self.prev_data["time"] = self.data["time"]
        self.data["time"] = t
        return
    
    def update_distance(self):
        # Ensure the required keys are present in both data dictionaries
        if "distance" not in self.data or "time" not in self.data or "speed" not in self.data:
            print("Missing data in self.data")
            return

        try:
            # Calculate the new distance
            time_difference = (self.data["time"] - self.prev_data["time"]) / 3600.0  # Convert seconds to hours
            distance = self.data["distance"] + time_difference * self.data["speed"]  # km

            # Update distances
            self.data["distance"] = distance

            print(f"Calculated time delta: {time_difference}")
            print(f"Calculated distance: {distance}")
        except Exception as e:
            print(f"Failed to update distance: {e}")

        return

    
    # def update_speed(self):
    #     dt = self.data["time"] - self.prev_data["time"]
    #     dt = dt / 1000 / 60 / 60  # convert ms to h
    #     ds = (self.data["distance"] - self.prev_data["distance"])
    #     ds = ds / 1000  #convert from m to km
    #     v = ds / dt

    #     self.prev_data["speed"] = self.data["speed"]
    #     self.data["speed"] = v
    #     return

    # def board_setup(self):
    #     connected = False
    #     while not connected:
    #         try:
    #             self.board = telemetrix.Telemetrix("COM3", 1, shutdown_on_exception=False)
    #             connected = True
    #             print("Successfully connected to Telemetrix.")
    #         except Exception as e:
    #             print(f"Connection failed with error: {e}. Retrying...")
    #             time.sleep(1)  # Wait a bit before retrying to avoid spamming connection attempts

    def solar_panel_serial_setup(self):
        try:
            self.solar_panel_1_serial = serial.Serial('COM4', 19200)
            self.connection_status['solar1']['ok'] = True
        except Exception as e:
            self.solar_panel_1_serial = None
            self.connection_status['solar1'].update(ok=False, err=str(e))

        try:
            self.solar_panel_2_serial = serial.Serial('COM10', 19200)
            self.connection_status['solar2']['ok'] = True
        except Exception as e:
            self.solar_panel_2_serial = None
            self.connection_status['solar2'].update(ok=False, err=str(e))

    def read_serial_data(self, ser, key):
        data = {}
        try:
            iterations = 0
            while ser.in_waiting and iterations < 10:
                line = ser.readline().decode('latin-1').strip()
                if line:
                    # Split the line based on any whitespace or common delimiters
                    parts = re.split(r'[\t,;| ]+', line)
                    if len(parts) == 2:
                        line_key = parts[0]
                        line_value = parts[1]
                        data[line_key] = line_value
                    else:
                        print(f"Line format error: Not enough parts - Line: {line}")
                iterations += 1
            ser.reset_input_buffer()  # Clear the buffer after reading       
            self.connection_status[key].update(ok=True, err=None)
        except Exception as e:
            self.connection_status[key].update(ok=False, err=str(e))
        return data
    
    def update_solar_panel(self):
        data1 = self.read_serial_data(self.solar_panel_1_serial, 'solar1')
        data2 = self.read_serial_data(self.solar_panel_2_serial, 'solar2')

        print("Solar panel: ")
        print(data1)
        print(data2)

        # Combine the data
        try:
            if "V" in data1:
                self.data['V'] = float(data1['V'])  # V should be the same for both panels
            if "V" in data2:
                self.data['V'] = float(data2['V'])  # V should be the same for both panels

            if "I" in data1:
                self.data['I_1'] = float(data1['I'])
            if "I" in data2:
                self.data['I_2'] = float(data2['I'])
            self.data["I"] = self.data["I_1"] + self.data["I_2"]

            if "PPV" in data1:
                self.data['PPV_1'] = float(data1['PPV'])
            if "PPV" in data2:
                self.data['PPV_2'] = float(data2['PPV'])
            self.data['PPV'] = self.data['PPV_1'] + self.data['PPV_2']

        except Exception as e:
            print(f"Failed to update solar panel data: {e}")

    def gps_setup(self):
        try:
            self.stream = serial.Serial('COM12', 115200, timeout=0)
            self.gps_reader = NMEAReader(self.stream)
            self.connection_status['gps']['ok'] = True
        except Exception as e:
            self.stream = None
            self.gps_reader = None
            self.connection_status['gps'].update(ok=False, err=str(e))

    def update_gps(self):
        raw_data, parsed_data = self.gps_reader.read()
        if parsed_data is not None:
            try:
                # print(raw_data)
                if hasattr(parsed_data, 'lat'):
                    print("lat: " + str(parsed_data.lat)) 
                    print("long: " + str(parsed_data.lon))
                    self.data["gps"] = [parsed_data.lat, parsed_data.lon]
                    self.connection_status['gps'].update(ok=True, err=None)
                else:
                    self.connection_status['gps'].update(ok=False, err="Parsed data does not contain lat or lon attributes.")
                    print("Parsed data does not contain lat or long attributes.")

                if  hasattr(parsed_data, 'spd'):
                    print("spd: " + str(parsed_data.spd))
                    if parsed_data.spd != 0.0:
                        self.data["speed"] = parsed_data.spd * 1.852 # km/h
                else:
                    self.connection_status['gps'].update(ok=False, err="Parsed data does not contain spd attribute.")
                    print("Parsed data does not contain spd attribute.")
            except Exception as e:
                self.connection_status['gps'].update(ok=False, err=str(e))
                print(f"Failed to update gps data: {e}")
        else:
            self.connection_status['gps'].update(ok=False, err="No GPS data received.")
            print("No gps message.")
            pass

        #update lap
        if time.time() - self.gps_prev_t > 20 and self.data["gps"] != ['', '']:
            pos = self.data["gps"]
            #check if we are in the starting area
            if GPS_BOUNDS[0][0] > pos[0] > GPS_BOUNDS[1][0] and GPS_BOUNDS[0][1] > pos[1] > GPS_BOUNDS[1][1]: #check for x and check for y
                self.data["lap"] += 1
                self.gps_prev_t = time.time()
                print("Lap detected. Reseting timer to:" + str(self.gps_prev_t))

    def battery_serial_setup(self):
        try:
            self.battery_serial = serial.Serial('COM3', 19200, timeout=0)
            self.connection_status['battery']['ok'] = True
        except Exception as e:
            self.battery_serial = None
            self.connection_status['battery'].update(ok=False, err=str(e))

    
    def update_battery(self):
        data = self.read_serial_data(self.battery_serial, 'battery')

        print("Battery: ")
        print(data)
        # Combine the data
        try:
            if "V" in data:
                self.data['battery'] = float(data['V'])
            if "I" in data:
                self.data['battery_I'] = float(data['I'])

        except Exception as e:
            print(f"Failed to update battery data: {e}")


    # def encoder_callback(self, data):
    #     """
    #     A callback function to report data changes.
    #     This will print the pin number, its reported value and
    #     the date and time when the change occurred

    #     :param data: [pin, current reported value, pin_mode, timestamp]
    #     """

    #     #update
    #     self.prev_encoder = self.encoder
    #     self.encoder = data[CB_VALUE]

    #     #update distance
    #     if (self.prev_encoder != self.encoder) and (self.prev_encoder == 1):
    #         self.rotation += 1

    #     date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    #     print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')
    #     return

    # def speed_encoder_setup(self, my_board, pin):
    #     """
    #     This function establishes the pin as a
    #     digital input. Any changes on this pin will
    #     be reported through the call back function.

    #     :param my_board: a telemetrix instance
    #     :param pin: Arduino pin number
    #     """

    #     # set the pin mode
    #     my_board.set_pin_mode_digital_input(pin, self.encoder_callback)

    # def dht_callback(self, data):
    #     # noinspection GrazieInspection
    #     """
    #     The callback function to display the change in distance
    #     :param data: [report_type = PrivateConstants.DHT, error = 0, pin number,
    #     dht_type, humidity, temperature timestamp]
    #                 if this is an error report:
    #                 [report_type = PrivateConstants.DHT, error != 0, pin number, dht_type
    #                 timestamp]
    #     """
    #     if data[1]:
    #         # error message
    #         date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[4]))
    #         print(f'DHT Error Report:'
    #             f'Pin: {data[2]} DHT Type: {data[3]} Error: {data[1]}  Time: {date}')
    #     else:
    #         self.prev_data["temperature"] = self.data["temperature"]
    #         self.data["temperature"] = data[5]
    #         date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[6]))
    #         print(f'DHT Valid Data Report:'
    #             f'Pin: {data[2]} DHT Type: {data[3]} Humidity: {data[4]} Temperature:'
    #             f' {data[5]} Time: {date}')
            
    # def dht_setup(self, my_board, pin, callback, dht_type):
    #     """
    #     Set the pin mode for a DHT 22 device. Results will appear via the
    #     callback.

    #     :param my_board: an telemetrix instance
    #     :param pin: Arduino pin number
    #     :param callback: The callback function
    #     :param dht_type: 22 or 11
    #     """

    #     # setup the DHT device
    #     try:
    #         my_board.set_pin_mode_dht(pin, callback, dht_type)
    #     except Exception as e:
    #         print(f"Failed to setup DHT device: {e}")

    # def battery_callback(self, data):
    #     """
    #     A callback function to report data changes.
    #     This will print the pin number, its reported value and
    #     the date and time when the change occurred

    #     :param data: [pin, current reported value, pin_mode, timestamp]
    #     """
    #     self.prev_data["battery"] = self.data["battery"]
    #     self.data["battery"] = data[CB_VALUE] * 5.0 # the sensor convert voltage range 0-25 to 0-5, so we have to convert it back
        
    #     date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    #     print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')

    # def battery_voltmeter_setup(self, my_board, pin):
    #     """
    #     This function establishes the pin as an
    #     analog input. Any changes on this pin will
    #     be reported through the call back function.

    #     :param my_board: a telemetrix instance
    #     :param pin: Arduino pin number
    #     """

    #     # set the pin mode
    #     my_board.set_pin_mode_analog_input(pin, differential=0, callback=self.battery_callback)

#TODO low voltage warning system: if battery voltage is below 11.2V, enable a warning signal connected to a digital pin

    
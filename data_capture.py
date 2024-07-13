# data_capture.py
import serial
import time
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
GPS_BOUNDS = ((33.03467, -97.28418), (33.03458, -97.28470))

# solar panel data keys
desired_ports = ['V', 'I', 'PPV']

class DataCapture:
    def __init__(self):
        self.start_time = time.time()
        self.gps_prev_t = time.time()

        self.encoder = False
        self.prev_encoder = False
        self.rotation = 0

        #data that will be displayed
        self.data = {
            "speed": 0,
            "distance": 0,
            "temperature": 0,
            "time": 0,
            "battery": 0,
            "lap": 0,
            'V': 0,
            'I': 0,
            'PPV': 0,
            "gps": [0,0],
            "gps_bounds": GPS_BOUNDS
        }
 
        self.prev_data = self.data

        self.board = None
        self.solar_panel_1_serial = None
        self.solar_panel_2_serial = None
        self.gps_serial = None
        self.gps_reader = None

        # self.board_setup()
        # self.dht_setup(self.board, DHT_PIN, self.dht_callback, 11)
        # self.speed_encoder_setup(self.board, ENCODER_PIN)    
        # self.battery_voltmeter_setup(self.board, BATTERY_VOLTMETER_PIN)
        self.solar_panel_serial_setup()
        self.gps_setup()

    def get_data(self):
        self.update_data()
        return self.data

    def update_data(self):
        #order matters
        self.update_time()
        self.update_distance()
        # self.update_speed()
        #temperature is updated in the callback
        #battery is updated in the callback
        self.update_solar_panel()
        self.update_gps()
        # self.update_lap()
    
    def update_time(self):
        t = time.time() - self.start_time
        t /= 60
        self.prev_data["time"] = self.data["time"]
        self.data["time"] = t
        return
    
    def update_distance(self):
        #update distance
        # distance = self.rotation * WHEEL_DIAMETER # m

        distance = self.prev_data["distance"] + (self.prev_data["time"] - self.data["time"]) / 360 * self.data["speed"] # km

        self.prev_data["distance"] = self.data["distance"]
        self.data["distance"] = distance
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
            self.solar_panel_2_serial = serial.Serial('COM10', 19200)
        except Exception as e:
            print(f"Solar panels serial port connection failed: {e}")

    def read_serial_data(self, ser):
        data = {}
        try:
            line = ser.readline().decode('latin-1').strip()
            line_key, line = line.split('\t')
            data[line_key] = line
                
        except Exception as e:
            print(f"Failed to read data from serial port: {e}")
        return data
    
    def update_solar_panel(self):
        data1 = self.read_serial_data(self.solar_panel_1_serial)
        data2 = self.read_serial_data(self.solar_panel_2_serial)

        # Combine the data
        try:
            self.data['V'] = float(data1['V'])  # V should be the same for both panels
            if data1['I'] != 'NA' and data2['I'] != 'NA':
                self.data['I'] = float(data1['I']) + float(self.data2['I'])

            if data1['PPV'] != 'NA' and data2['PPV'] != 'NA':
                self.data['PPV'] = float(data1['PPV']) + float(data2['PPV'])
        except Exception as e:
            print(f"Failed to update solar panel data: {e}")

    def gps_setup(self):
        self.stream = serial.Serial('COM7', 115200, timeout=3)
        self.gps_reader = NMEAReader(self.stream)

    def update_gps(self):
        raw_data, parsed_data = self.gps_reader.read()
        if parsed_data is not None:
            try:
                print(raw_data)
                if hasattr(parsed_data, 'lat'):
                    print("lat: " + str(parsed_data.lat)) 
                    print("long: " + str(parsed_data.lon))
                    self.data["gps"] = [parsed_data.lat, parsed_data.lon]
                if  hasattr(parsed_data, 'spd'):
                    print("spd: " + str(parsed_data.spd))
                    self.data["speed"] = parsed_data.spd * 1.852 # km/h
                else:
                    print("Parsed data does not contain lat, long, or spd attributes.")
            except Exception as e:
                print(f"Failed to update gps data: {e}")
        else:
            print("No gps message.")
            pass

        if time.time() - self.gps_prev_t > 20:
            pos = self.data["gps"]
            #check if we are in the starting area
            if GPS_BOUNDS[0][0] > pos[0] > GPS_BOUNDS[1][0] and GPS_BOUNDS[0][1] > pos[1] > GPS_BOUNDS[1][1]: #check for x and check for y
                self.data["lap"] += 1
                self.gps_prev_t = time.time()
                print("Lap detected. Reseting timer to:" + str(self.gps_prev_t))


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

    
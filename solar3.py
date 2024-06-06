import os
import serial
from collections.abc import Callable
from tkinter import *
from typing import Tuple
import numpy as np
import cv2
from PIL import Image, ImageTk
import sys
import time
from telemetrix import telemetrix

# Touch sensor pin#
DIGITAL_PIN = 7  # arduino pin number

#dht sensor pin#
DHT_PIN = 4

# Battery Sensor pin#
ANALOG_PIN = 5


# Telemetrix Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

# GPS counter range (x0,y0,x1,y1)
gps_bounds = (33.03467, -97.28418, 33.03458, -97.28470)

class VideoWidget(Frame):
    def __init__(self, parent, video_source=0):
        super().__init__(parent)
        self.video_source = video_source
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # width = 1024    
        # height = 600
        # self.video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


        self.video_label = Label(self)
        self.video_label.pack()
        
        self.speed_label = Label(self, text="Speed: ", font=('Arial', 40))
        self.speed_label.place(x=20, y=30)

        self.distance_label = Label(self, text="Distance: ", font=('Arial', 30))
        self.distance_label.place(x=20, y=100)

        self.temp_label = Label(self, text="Temperature: ", font=('Arial', 30))
        self.temp_label.place(x=20, y=170)

        self.time_label = Label(self, text="Time: ", font=('Arial', 30))
        self.time_label.place(x=20, y=240)

        self.battery_label = Label(self, text="Battery: ", font=('Arial', 30))
        self.battery_label.place(x=20, y=280)

        self.lap_label = Label(self, text="Lap: ", font=('Arial', 30))
        self.lap_label.place(x=20, y=320)

        self.serial_data_label = Label(self, text="", font=('Arial', 30))  # Add a label for serial data
        self.serial_data_label.place(x=20, y=360)
        
        #self.next_data_button = Button(self, text="Next Data", font=('Arial', 20), command=self.show_next_data)
        #self.next_data_button.place(x=20, y=380)

        self.pack()
        self.update()



    def update(self):
        init_time = time.time()
        ret, frame = self.video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            frame = cv2.resize(frame, (1024, 600), cv2.INTER_AREA)
            frame = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=frame)
            self.video_label.configure(image=photo)
            self.video_label.image = photo
        #print(time.time() - init_time)

        # self.solar.update()

        # self.after(5, self.update)

    def update_info_labels(self, speed_str, distance_str, temp_str, time_str):
        self.speed_label.config(text=speed_str)
        self.distance_label.config(text=distance_str)
        self.temp_label.config(text=temp_str)
        self.time_label.config(text=time_str)

    def update_serial_data_label(self, serial_data):
        self.serial_data_label.config(text=serial_data)  # Update serial data label



desired_ports = ['V', 'I', 'PPV']

class SolarCar(object):

    def __init__(self,
                 get_speed: Callable,
                 get_pos: Callable,
                 gps_bounds: Tuple,
                 get_touch: Callable,
                 one_cycle_len: float,
                 get_temp: Callable,
                 live_video: Callable,
                 serial_ports: Tuple[str, str],  # Default serial port
                 baud_rate: int = 19200):  # Pass the VideoWidget instance
        if (gps_bounds[0] < gps_bounds[2]) or (gps_bounds[1] < gps_bounds[3]):
            print('Wrong GPS boundary')
            sys.exit(1)
        self.root = Tk()
        self.root.geometry('1920x1080') #reverted back to original
        self.root.title('Kent Solar Car')

        self.video_widget = VideoWidget(self.root, video_source=0)
        self.setup_serial_communication(serial_ports, baud_rate)

        self.data = {key: 'NA' for key in desired_ports}
        self.data_2 = {key: 'NA' for key in desired_ports}  # For second serial port
        self.combined_data = {key: 'NA' for key in desired_ports}  # Combined data

        self.update_serial_data_label() 
        self.update_serial_data_label_str()
        

        self.frame = Frame(self.root)
        self.frame.pack()

        self.speed_update_interval = 1000
        self.is_km = 1
        self.previous_distance = 0
        self.distance = 0
        self.start_time = time.time()
        self.one_cycle_len = one_cycle_len
        self.get_touch = get_touch
        self.gps_dim = gps_bounds
        self.get_speed = get_speed
        self.get_pos = get_pos
        self.get_temp = get_temp
        self.live_video = live_video
        self.rot_counter = 0
        self.previous_state = 1
        self.speed_str = StringVar()
        self.touch_sensor_str = StringVar()
        self.time_str = StringVar()
        self.temp_str = StringVar()

        self.gps_prev_t = 0.0
        self.lap = 0
        # self.update_speed()
        # self.update_distance()
        # self.update_temp()
        # self.update_time()

    def setup_serial_communication(self, serial_ports, baud_rate):
        #self.ser1 = serial.Serial(serial_ports[0], baud_rate)
        #self.ser2 = serial.Serial(serial_ports[1], baud_rate)
        try:
            self.ser1 = serial.Serial('COM4', 19200)
            self.ser2 = serial.Serial('COM5', 19200)
        except:
            return

    def read_serial_data(self, ser):
        data = {}
        try:
            line = ser.readline().decode('latin-1').strip()
            line_key, line = line.split('\t')
            if line_key in desired_ports:
                data[line_key] = line
        except Exception as e:
            print(f"Failed to read data from serial port: {e}")
        return data
    

    def update_serial_data_label(self):
        try:
            data1 = self.read_serial_data(self.ser1)
            data2 = self.read_serial_data(self.ser2)

            for key in desired_ports:
                if key in data1:
                    self.data[key] = data1[key]
                if key in data2:
                    self.data_2[key] = data2[key]

            # Combine the data
            self.combined_data['V'] = self.data['V']  # V remains unchanged
            if self.data['I'] != 'NA' and self.data_2['I'] != 'NA':
                self.combined_data['I'] = str(float(self.data['I']) + float(self.data_2['I']))
            else:
                self.combined_data['I'] = 'NA'
            if self.data['PPV'] != 'NA' and self.data_2['PPV'] != 'NA':
                self.combined_data['PPV'] = str(float(self.data['PPV']) + float(self.data_2['PPV']))
            else:
                self.combined_data['PPV'] = 'NA'

            # self.root.after(200, self.update_serial_data_label)
        except:
            print('No COM')
            return

    def update_serial_data_label_str(self):
        try:
            tmp = ''
            for line_key in desired_ports:
                if line_key == 'V' and self.combined_data[line_key] != 'NA':
                    tmp += f'{line_key}: {float(self.combined_data[line_key]) / 1000} | '
                else:
                    tmp += f'{line_key}: {self.combined_data[line_key]} | '
            self.video_widget.update_serial_data_label(tmp)
            # self.root.after(1000, self.update_serial_data_label_str)
        except:
            return

    def update_temp(self):
        # try:
        c, f = self.get_temp()
        self.temp_str.set(f'Temp: {c:.2f} C | {f:.2f} F')
        self.video_widget.update_info_labels(self.speed_str.get(), self.touch_sensor_str.get(), self.temp_str.get(), self.time_str.get())  # Update VideoWidget
        # self.root.after(1000, self.update_temp)

        #this is jank but I'm putting the battery update here as well
        self.video_widget.battery_label.config(text= "Battery: " + str(curr_battery) + "V")

        # I guess I'm putting GPS here as well
        #TODO allow the car to park in the starting area without counting
        #only check every 20 seconds to only count once
        if time.time() - self.gps_prev_t > 20:
            #check if we are in the starting area
            pos = get_pos()
            try:
                if gps_bounds[0] < pos[0] < gps_bounds[2] and gps_bounds[1] < pos[1] < gps_bounds[3]:
                    self.lap += 1
                    self.gps_prev_t = time.time()
            except:
                print("GPS failed")
        self.video_widget.battery_label.config(text= "Lap: " + str(self.lap) )
            
        # except:
            # return


    def update_time(self):
        x = time.time() - self.start_time
        x /= 60
        self.time_str.set(f'Time: {x:.2f} min')
        self.video_widget.update_info_labels(self.speed_str.get(), self.touch_sensor_str.get(), self.temp_str.get(), self.time_str.get())  # Update VideoWidget
        # self.root.after(500, self.update_time)

        

    def update_distance(self):
        x = self.get_touch()
        if (self.previous_state != x) and (self.previous_state == 1):
            self.rot_counter += 1
        self.previous_state = x
        distance = self.rot_counter * self.one_cycle_len / 1000
        if self.is_km:
            self.touch_sensor_str.set(f'Distance: {distance:.3f} km')
        else:
            self.touch_sensor_str.set(f'Distance: {(distance / 1.61):.3f} mil ')
        self.distance = self.rot_counter * self.one_cycle_len
        self.video_widget.update_info_labels(self.speed_str.get(), self.touch_sensor_str.get(), self.temp_str.get(), self.time_str.get())  # Update VideoWidget
        # self.root.after(1, self.update_distance)

    def update_speed(self):
        # get current time
        time_passed = self.speed_update_interval / 1000 / 60 / 60  # h
        distance_covered = (self.distance - self.previous_distance) / 1000  # km
        current_speed = distance_covered / time_passed

        if self.is_km:
            self.speed_str.set(f'Speed: {current_speed:.2f} kmph')
        else:
            self.speed_str.set(f'Speed: {current_speed / 1.61:.3f} mph')
        self.previous_distance = self.distance
        self.video_widget.update_info_labels(self.speed_str.get(), self.touch_sensor_str.get(), self.temp_str.get(), self.time_str.get())  # Update VideoWidget
        # self.root.after(self.speed_update_interval, self.update_speed)

    def start_loop(self):
        self.root.mainloop()

    def update(self):
        self.update_distance()
        self.update_speed()
        self.update_temp()
        self.update_time()

def get_speed():
    return float(np.random.rand())

GPS = serial.Serial("COM7", 115200)

curr_pos = []

def to_degree(s):
    degree = s[:2]
    minuit = s[2:]
    try:
        return float(degree) + (float(minuit) / 60)
    except ValueError:
        return 0, 0

def get_pos():
    # x_len = gps_dim[2] - gps_dim[0]
    # y_len = gps_dim[3] - gps_dim[1]
    # x_base = gps_dim[0]
    # y_base = gps_dim[1]

    gps_data = []

    for i in range(6):
        line = GPS.readline().decode('latin-1').strip().split(',')
        if line[0] == "$GPRMC":
            print("GPS data recieved")

            curr_pos = [to_degree(line[4]), to_degree(line[5])]
            break

    return curr_pos[0], curr_pos[1]

    # return float(np.random.rand() * x_len + x_base), float(np.random.rand() * y_len + y_base)

curr_touch = False

def touch_sensor_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    curr_touch = data[CB_VALUE]
    print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')


def digital_in(my_board, pin):
    """
     This function establishes the pin as a
     digital input. Any changes on this pin will
     be reported through the call back function.

     :param my_board: a telemetrix instance
     :param pin: Arduino pin number
     """

    # set the pin mode
    my_board.set_pin_mode_digital_input(pin, touch_sensor_callback)
    # time.sleep(1)
    # my_board.disable_all_reporting()
    # time.sleep(4)
    # my_board.enable_digital_reporting(12)

    # time.sleep(3)
    # my_board.enable_digital_reporting(pin)
    # time.sleep(1)

def get_touch_sensor(input_pin=DIGITAL_PIN):
    try:
        return curr_touch
    except:
        return

curr_battery = 0.0

def battery_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    curr_battery = data[CB_VALUE] * 5 # the sensor convert voltage range 0-25 to 0-5, so we have to convert it back
    print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')


def analog_in(my_board, pin):
    """
     This function establishes the pin as an
     analog input. Any changes on this pin will
     be reported through the call back function.

     :param my_board: a telemetrix instance
     :param pin: Arduino pin number
     """

    # set the pin mode
    my_board.set_pin_mode_analog_input(pin, differential=5, callback=battery_callback)

    # time.sleep(5)
    # my_board.disable_analog_reporting()
    # time.sleep(5)
    # my_board.enable_analog_reporting()

def dht(my_board, pin, callback, dht_type):
    # noinspection GrazieInspection
    """
        Set the pin mode for a DHT 22 device. Results will appear via the
        callback.

        :param my_board: an telemetrix instance
        :param pin: Arduino pin number
        :param callback: The callback function
        :param dht_type: 22 or 11
        """

    # set the pin mode for the DHT device
    try:
        my_board.set_pin_mode_dht(pin, callback, dht_type)
    except:
        pass

curr_temp = 0.0

def dht_callback(data):
    # noinspection GrazieInspection
    """
        The callback function to display the change in distance
        :param data: [report_type = PrivateConstants.DHT, error = 0, pin number,
        dht_type, humidity, temperature timestamp]
                     if this is an error report:
                     [report_type = PrivateConstants.DHT, error != 0, pin number, dht_type
                     timestamp]
        """
    if data[1]:
        # error message
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[4]))
        print(f'DHT Error Report:'
              f'Pin: {data[2]} DHT Type: {data[3]} Error: {data[1]}  Time: {date}')
    else:
        curr_temp = data[5]
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[6]))
        print(f'DHT Valid Data Report:'
              f'Pin: {data[2]} DHT Type: {data[3]} Humidity: {data[4]} Temperature:'
              f' {data[5]} Time: {date}')

def get_temp():
    # print('1')
    try:
        temperature_c = curr_temp
        # print(curr_temp)
        temperature_f = 9/5 * curr_temp + 32 #converting C to F
        return temperature_c, temperature_f
    except:
        print('Temp Sensor failure')
        return -1, -1


#video = cv2.VideoCapture(0)
def live_video():
    ret, image = solar.video.read()
    if not ret:
        print('video_failed')
    else:
        return image

#video_widget = VideoWidget(self.root)  # Create an instance of VideoWidget.py


Connected = False

#connect telemetrix
while not Connected:
    try:
        board = telemetrix.Telemetrix("COM3", 1)
        Connected = True

    # except RuntimeError:
        # exit(0)

    except:
        os.execv(sys.argv[0], sys.argv)
        exit(0)
        print("Connection failed, retrying")

#wait for dht to go online
# time.sleep(1)

#setup telemetrix inputs
dht(board, DHT_PIN, dht_callback, 11)
digital_in(board, DIGITAL_PIN)    
analog_in(board, ANALOG_PIN)

solar = SolarCar(get_speed, get_pos, gps_bounds, get_touch_sensor, 2.153412, get_temp, live_video, serial_ports=['COM4', ''], baud_rate=19200)  # Pass video_widget as an argument

# solar.start_loop()

while True:
    #this has the same effect as start_loop()
    solar.root.update_idletasks() 
    solar.root.update()

    #our code
    solar.update()
    solar.video_widget.update()

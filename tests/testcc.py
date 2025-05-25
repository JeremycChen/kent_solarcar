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

lap = 0

GPS = serial.Serial("COM12", 115200)

curr_pos = []

def get_pos():
    # x_len = gps_dim[2] - gps_dim[0]
    # y_len = gps_dim[3] - gps_dim[1]
    # x_base = gps_dim[0]
    # y_base = gps_dim[1]

    gps_data = []

    for i in range(6):
        line = GPS.readline().split(",")
        if line[0] == "$GPRMC":
            print("GPS data recieved")
            curr_pos = [line[2], line[3]]
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
        # print(f'DHT Valid Data Report:'
        #       f'Pin: {data[2]} DHT Type: {data[3]} Humidity: {data[4]} Temperature:'
        #       f' {data[5]} Time: {date}')

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

Connected = False

#connect telemetrix
while not Connected:
    try:
        board = telemetrix.Telemetrix("COM3", 1)
        Connected = True

    except RuntimeError:
        exit(0)

    except:
        print("Connection failed, retrying")

#wait for dht to go online
# time.sleep(1)

#setup telemetrix inputs
dht(board, DHT_PIN, dht_callback, 11)
digital_in(board, DIGITAL_PIN)    
analog_in(board, ANALOG_PIN)

#setup camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# width = 1920
# height = 1080
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

while(True): 
      
# Capture frame-by-frame 
    ret, frame = cap.read() 
    if ret == True: 
        #put text
        # frame = cv2.putText(frame, )

        # Display the resulting frame 
        cv2.imshow('Frame', frame) 
          
    # Press Q on keyboard to exit 
        if cv2.waitKey(25) & 0xFF == ord('q'): 
            break
  
# Break the loop 
    else: 
        break
  
# When everything done, release 
# the video capture object 
cap.release() 
  
# Closes all the frames 
cv2.destroyAllWindows() 
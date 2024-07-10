import cv2
import tkinter as tk
from PIL import Image, ImageTk
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

curr_touch = False
curr_battery = 0.0
curr_temp = 0.0

def dht(my_board, pin, callback, dht_type):
    try:
        my_board.set_pin_mode_dht(pin, callback, dht_type)
    except:
        pass

def touch_sensor_callback(data):
    global curr_touch
    curr_touch = data[CB_VALUE]

def digital_in(my_board, pin):
    my_board.set_pin_mode_digital_input(pin, touch_sensor_callback)

def battery_callback(data):
    global curr_battery
    curr_battery = data[CB_VALUE] * 5 / 2 * 0.01  # Convert voltage range 0-25 to 0-5

def analog_in(my_board, pin):
    my_board.set_pin_mode_analog_input(pin, differential=5, callback=battery_callback)

def dht_callback(data):
    global curr_temp
    if data[1] == 0:
        curr_temp = data[5]

def get_touch_sensor(input_pin=DIGITAL_PIN):
    return curr_touch

def get_temp():
    return curr_temp

def main():
    
    # Connect to Telemetrix
    Connected = False
    while not Connected:
        try:
            board = telemetrix.Telemetrix("COM3", 1)
            Connected = True
        except RuntimeError:
            exit(0)
        except:
            print("Connection failed, retrying")

    # Setup Telemetrix inputs
    dht(board, DHT_PIN, dht_callback, 22)
    digital_in(board, DIGITAL_PIN)
    analog_in(board, ANALOG_PIN)

    # Setup GUI
    root = tk.Tk()
    root.title("Solar Car Dashboard")

    # Create labels for displaying sensor data
    touch_label = tk.Label(root, text="Touch Sensor: ")
    touch_label.pack()
    battery_label = tk.Label(root, text="Battery Voltage: ")
    battery_label.pack()
    temp_label = tk.Label(root, text="Temperature: ")
    temp_label.pack()

    # Function to update sensor data
    def update_data():
        touch_label.config(text="Touch Sensor: " + str(get_touch_sensor()))
        battery_label.config(text="Battery Voltage: " + str(curr_battery))
        temp_label.config(text="Temperature: " + str(get_temp()))
        root.after(100, update_data)  # Update data every 100 milliseconds

    update_data()

    # Display video feed
    video_label = tk.Label(root)
    video_label.pack()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    def stream_video():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            video_label.img = img
            video_label.config(image=img)
            video_label.after(10, stream_video)  # Update video every 10 milliseconds

    stream_video()

    root.mainloop()

if __name__ == "__main__":
    main()

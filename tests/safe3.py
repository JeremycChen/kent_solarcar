#create a python program running on latteapanda that streams live video from camera, from telemetrix import telemetrix (this is to communicate python with arduino), reads speed from Ardurino digital pin 7, reads temperature from Arduino digital pin 4, reads voltage from Arduino analog pin 5, reads gps from COM12 and displays as long and lat, read another voltage/power/and current from COM20 an COM10, display a GUI with camera footage as background and display all the data using labels on the GUIp
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from telemetrix import telemetrix
import serial
import cv2

# Constants
DIGITAL_PIN = 7  # Arduino pin number
DHT_PIN = 4  # DHT sensor pin
ANALOG_PIN = 5  # Battery sensor pin

# Telemetrix Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

curr_touch = False
curr_battery = 0.0
curr_temp = 0.0

class ArduinoThread(QThread):
    data_signal = pyqtSignal(int, int, int)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.board = None

    def run(self):
        try:
            self.board = telemetrix.Telemetrix(self.port, 1)
            self.board.set_pin_mode_digital_input(DIGITAL_PIN, self.touch_sensor_callback)
            self.board.set_pin_mode_analog_input(ANALOG_PIN, differential=5, callback=self.battery_callback)
            self.board.set_pin_mode_dht(DHT_PIN, self.dht_callback, 11)

            while True:
                speed = self.get_touch_sensor()
                temperature, _ = get_temp()
                voltage = self.curr_battery
                self.data_signal.emit(speed, temperature, voltage)

        except Exception as e:
            print(f"Error in ArduinoThread: {e}")
        finally:
            if self.board:
                self.board.close()

    def touch_sensor_callback(self, data):
        self.curr_touch = data[CB_VALUE]

    def get_touch_sensor(self):
        return self.curr_touch

    def battery_callback(self, data):
        self.curr_battery = data[CB_VALUE] * 5  # Convert voltage range 0-25 to 0-5

    def dht_callback(self, data):
        if not data[1]:
            self.curr_temp = data[5]

def get_temp():
    return curr_temp, 9/5 * curr_temp + 32  # Converting C to F

class VideoThread(QThread):
    frame_signal = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_signal.emit(qt_image)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Video and Data Display")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)

        self.data_label = QLabel()
        self.data_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.data_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.arduino_thread = ArduinoThread("COM3")
        self.arduino_thread.data_signal.connect(self.update_data)
        self.arduino_thread.start()

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.update_frame)
        self.video_thread.start()

    def update_data(self, speed, temperature, voltage):
        data_text = f"Speed: {speed} km/h\nTemperature: {temperature}°C\nVoltage: {voltage} V"
        self.data_label.setText(data_text)

    def update_frame(self, frame):
        pixmap = QPixmap.fromImage(frame)
        self.video_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

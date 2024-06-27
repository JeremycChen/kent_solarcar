import cv2
import serial
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from telemetrix import telemetrix

# Constants
ARDUINO_PORT = 'COM3'  # Replace with the appropriate port for your Arduino
GPS_PORT = 'COM7'  # Replace with the appropriate port for your GPS module
POWER_PORT_1 = 'COM4'  # Replace with the appropriate port for your first power sensor
POWER_PORT_2 = 'COM10'  # Replace with the appropriate port for your second power sensor

# Thread for reading data from Arduino
class ArduinoThread(QThread):
    data_signal = pyqtSignal(int, int, int)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.arduino = None

    def run(self):
        try:
            self.arduino = serial.Serial(self.port, 9600)
            while True:
                data = self.arduino.readline().decode().strip().split(',')
                if len(data) == 3:
                    speed, temperature, voltage = map(int, data)
                    self.data_signal.emit(speed, temperature, voltage)
        except Exception as e:
            print(f"Error in ArduinoThread: {e}")
        finally:
            if self.arduino:
                self.arduino.close()

# Thread for reading data from GPS module
class GPSThread(QThread):
    gps_signal = pyqtSignal(str, str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.gps = None

    def run(self):
        try:
            self.gps = serial.Serial(self.port, 9600)
            while True:
                data = self.gps.readline().decode().strip().split(',')
                if len(data) >= 4:
                    latitude, longitude = data[2], data[3]
                    self.gps_signal.emit(latitude, longitude)
        except Exception as e:
            print(f"Error in GPSThread: {e}")
        finally:
            if self.gps:
                self.gps.close()

# Thread for reading data from power sensors
class PowerThread(QThread):
    power_signal = pyqtSignal(int, int)

    def __init__(self, port1, port2):
        super().__init__()
        self.port1 = port1
        self.port2 = port2
        self.power1 = None
        self.power2 = None

    def run(self):
        try:
            self.power1 = serial.Serial(self.port1, 9600)
            self.power2 = serial.Serial(self.port2, 9600)
            while True:
                voltage1 = int(self.power1.readline().decode().strip())
                voltage2 = int(self.power2.readline().decode().strip())
                self.power_signal.emit(voltage1, voltage2)
        except Exception as e:
            print(f"Error in PowerThread: {e}")
        finally:
            if self.power1:
                self.power1.close()
            if self.power2:
                self.power2.close()

# Main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Video and Data Display")
        self.setGeometry(100, 100, 800, 600)

        # Create layout and widgets
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)

        self.data_label = QLabel()
        self.data_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.video_label)
        layout.addWidget(self.data_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Start threads
        self.arduino_thread = ArduinoThread(ARDUINO_PORT)
        self.arduino_thread.data_signal.connect(self.update_data)
        self.arduino_thread.start()

        self.gps_thread = GPSThread(GPS_PORT)
        self.gps_thread.gps_signal.connect(self.update_gps)
        self.gps_thread.start()

        self.power_thread = PowerThread(POWER_PORT_1, POWER_PORT_2)
        self.power_thread.power_signal.connect(self.update_power)
        self.power_thread.start()

        # Start video capture
        self.video_capture = cv2.VideoCapture(0)  # Replace 0 with the appropriate camera index
        self.video_timer = self.startTimer(30)  # Update video every 30 milliseconds

    def update_data(self, speed, temperature, voltage):
        data_text = f"Speed: {speed} km/h\nTemperature: {temperature}°C\nVoltage: {voltage} V"
        self.data_label.setText(data_text)

    def update_gps(self, latitude, longitude):
        gps_text = f"Latitude: {latitude}, Longitude: {longitude}"
        self.data_label.setText(self.data_label.text() + "\n" + gps_text)

    def update_power(self, voltage1, voltage2):
        power_text = f"Power 1: {voltage1} V, Power 2: {voltage2} V"
        self.data_label.setText(self.data_label.text() + "\n" + power_text)

    def timerEvent(self, event):
        ret, frame = self.video_capture.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.arduino_thread.quit()
        self.gps_thread.quit()
        self.power_thread.quit()
        self.video_capture.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
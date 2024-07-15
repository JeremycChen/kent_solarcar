import sys
import datetime
import atexit

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout 
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QFont
from PyQt5 import QtWebEngineWidgets
import folium
import cv2

import data_capture


DISABLE_DATA_CAPTURE = False
DISABLE_CAMERA = False

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        if not DISABLE_DATA_CAPTURE:
            self.data_capture = data_capture.DataCapture()
        atexit.register(self.exit_handler)
        self.initUI()

    def exit_handler(self):
        # self.front_video.release()
        self.back_video.release()
        cv2.destroyAllWindows()
        
        # self.data_capture.board.shutdown()
        print ('Exit sucessful')

    def initUI(self):
        # Set window size and title
        self.setGeometry(0, 0, 1024, 200)
        self.setWindowTitle('Dashboard')

        # Create layout
        canvas = QHBoxLayout()
        left = QVBoxLayout()
        data_table_layout = QGridLayout()
        canvas.addLayout(left)
        self.setLayout(canvas)

        self.map = folium.Map(location=[45.5236, -122.6750], zoom_start=15)
        self.map_widget = QtWebEngineWidgets.QWebEngineView()
        self.map_widget.setHtml(self.map.get_root().render())
        canvas.addWidget(self.map_widget)

        # Define labels
        self.speed_label = QLabel('Speed: 0 km/h | 0 mph')
        self.distance_label = QLabel('Distance: 0 km')
        self.time_label = QLabel('Time: 0')
        self.lap_count_label = QLabel('Lap Count: 0')

        self.battery_voltage_label = QLabel('Battery V: 0mV')
        self.battery_current_label = QLabel('Battery I: 0mV')
        self.temperature_label = QLabel('Temperature: 0°C')

        self.panel_current_label = QLabel('Panel I: 0mA')
        self.panel_ppv_label = QLabel('Panel PPV: 0W')
        self.panel_voltage_label = QLabel('Panel V: 0mV')


        # Set font size for labels
        font = QFont('Arial', 15)
        large_font = QFont('Arial', 40)

        self.speed_label.setFont(large_font)
        self.distance_label.setFont(font)
        self.time_label.setFont(font)
        self.lap_count_label.setFont(font)

        self.battery_voltage_label.setFont(font)
        self.battery_current_label.setFont(font)
        self.temperature_label.setFont(font)

        self.panel_current_label.setFont(font)
        self.panel_ppv_label.setFont(font)
        self.panel_voltage_label.setFont(font)

        # Add labels to layout
        left.addWidget(self.speed_label)
        left.addLayout(data_table_layout)

        data_table_layout.addWidget(self.distance_label, 1, 0)
        data_table_layout.addWidget(self.time_label, 2, 0)
        data_table_layout.addWidget(self.lap_count_label, 3, 0)

        data_table_layout.addWidget(self.battery_voltage_label, 1, 1)
        data_table_layout.addWidget(self.battery_current_label, 2, 1)
        data_table_layout.addWidget(self.temperature_label, 3, 1)

        data_table_layout.addWidget(self.panel_current_label, 1, 2)
        data_table_layout.addWidget(self.panel_ppv_label, 2, 2)
        data_table_layout.addWidget(self.panel_voltage_label, 3, 2)

        print("GUI setup good.")

        # Update time every second
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(1000)  # Update every 100 milliseconds

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.display_camera_streams)
        self.camera_timer.start(30) # about 30 fps

        # self.front_video = None
        self.back_video = None

        if not DISABLE_CAMERA : self.camera_setup()

    def camera_setup(self):
        # self.front_video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.back_video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.back_video.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        self.back_video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def display_camera_streams(self):

        if DISABLE_CAMERA: return

        # ret1, frame1 = self.front_video.read()
        ret2, frame2 = self.back_video.read()

        # if not ret1 or not ret2:
        #     print("Failed to capture video frames")
        #     return

        # cv2.imshow("Front Camera", frame1)
        cv2.imshow("Back Camera", frame2)

        if cv2.waitKey(1) == ord('q'):
            # self.front_video.release()
            self.back_video.release()
            cv2.destroyAllWindows()

    def update_data(self):
        if DISABLE_DATA_CAPTURE: return
        data = self.data_capture.get_data()
        print(data)
        # print(str(datetime.timedelta(seconds=data['time']))[:7])
        self.speed_label.setText('Speed: ' + str(round(data['speed'] * 0.621371,3)) + "mph")
        self.distance_label.setText('Distance: ' + str(round(data['distance'],3)) + ' km')
        self.temperature_label.setText('Temperature: ' + str(round(data['temperature'],3)) + '°C')
        self.time_label.setText('Time: ' + str(datetime.timedelta(seconds=data['time']))[:7])

        self.battery_voltage_label.setText('Battery V: ' + str(round(data['battery'],3)) + 'V')
        self.battery_current_label.setText('Battery I: ' + str(round(data['battery_I'],3)) + 'A')

        self.lap_count_label.setText('Lap Count: ' + str(round(data['lap'],3)))
        self.panel_current_label.setText('Panel I: ' + str(round(data['I'],3)) + 'mA')
        self.panel_ppv_label.setText('Panel PPV: ' + str(round(data['PPV'],3)) + 'W')
        self.panel_voltage_label.setText('Panel V: ' + str(round(data['V'],3)) + 'mV')

        self.map = folium.Map(location=data["gps"], zoom_start=15)
        folium.Marker(location=data["gps"], popup="Kent Solar Car").add_to(self.map)
        folium.Rectangle(
            bounds=data["gps_bounds"],
            line_join="bevel",
            dash_array="15, 10, 5, 10, 15",
            color="blue",
            line_cap= "round",
            fill= True,
            fill_color="red",
            weight=5,
            popup="Finish Line",
            tooltip= "<strong>Finish Line</strong>",
        ).add_to(self.map)

        self.map_widget.setHtml(self.map.get_root().render())

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()

    sys.exit(app.exec_())
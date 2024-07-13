import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QHBoxLayout 
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QFont
from PyQt5 import QtWebEngineWidgets
import folium
import cv2
import data_capture
import atexit
import datetime

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

        app.exec_()
        
        # self.data_capture.board.shutdown()
        print ('Exit sucessful')

    def initUI(self):
        # Set window size and title
        self.setGeometry(0, 0, 1024, 200)
        self.setWindowTitle('Dashboard')

        # Create layout
        canvas = QHBoxLayout()
        left = QGridLayout()
        canvas.addLayout(left)
        self.setLayout(canvas)

        self.map = folium.Map(location=[45.5236, -122.6750], zoom_start=15)
        self.map_widget = QtWebEngineWidgets.QWebEngineView()
        self.map_widget.setHtml(self.map.get_root().render())
        canvas.addWidget(self.map_widget)

        # Define labels
        self.speedLabel = QLabel('Speed: 0 km/h')
        self.distanceLabel = QLabel('Distance: 0 km')
        self.temperatureLabel = QLabel('Temperature: 0°C')
        self.timeLabel = QLabel('Time: 0')
        self.batteryLabel = QLabel('Battery: 0V')
        self.lapCountLabel = QLabel('Lap Count: 0')
        self.currentLabel = QLabel('Current (I): 0A')
        self.PPVoltageLabel = QLabel('PPV: 0V')
        self.VoltageLabel = QLabel('V: 0V')


        # Set font size for labels
        font = QFont('Arial', 10)
        large_font = QFont('Arial', 40)
        self.speedLabel.setFont(large_font)
        self.distanceLabel.setFont(font)
        self.temperatureLabel.setFont(font)
        self.timeLabel.setFont(font)
        self.batteryLabel.setFont(font)
        self.lapCountLabel.setFont(font)
        self.currentLabel.setFont(font)
        self.PPVoltageLabel.setFont(font)
        self.VoltageLabel.setFont(font)

        # Add labels to layout
        left.addWidget(self.speedLabel, 0, 0)
        left.addWidget(self.distanceLabel, 1, 0)
        left.addWidget(self.timeLabel, 2, 0)
        left.addWidget(self.lapCountLabel, 3, 0)

        # left.addWidget(self.batteryLabel, 1, 1)
        # left.addWidget(self.temperatureLabel, 2, 1)
        left.addWidget(self.currentLabel, 1, 1)
        left.addWidget(self.PPVoltageLabel, 2, 1)
        left.addWidget(self.VoltageLabel, 3, 1)

        print("GUI setup good.")

        # Update time every second
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(1000)  # Update every 20 milliseconds

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.display_camera_streams)
        self.camera_timer.start(30) # about 30 fps

        # self.front_video = None
        self.back_video = None

        if not DISABLE_CAMERA : self.camera_setup()

    def camera_setup(self):
        # self.front_video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.back_video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

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
        print(str(datetime.timedelta(seconds=data['time']))[:7])
        self.speedLabel.setText('Speed: ' + str(round(data['speed'],3)) + 'km/h')
        self.distanceLabel.setText('Distance: ' + str(round(data['distance'],3)) + ' km')
        self.temperatureLabel.setText('Temperature: ' + str(round(data['temperature'],3)) + '°C')
        self.timeLabel.setText('Time: ' + str(datetime.timedelta(seconds=data['time']))[:7])
        self.batteryLabel.setText('Battery: ' + str(round(data['battery'],3)) + 'V')
        self.lapCountLabel.setText('Lap Count: ' + str(round(data['lap'],3)))
        self.currentLabel.setText('Current (I): ' + str(round(data['I'],3)) + 'A')
        self.PPVoltageLabel.setText('PPV: ' + str(round(data['PPV'],3)) + 'V')
        self.VoltageLabel.setText('V: ' + str(round(data['V'],3)) + 'V')
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
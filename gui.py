import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QHBoxLayout 
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QFont
from PyQt5 import QtWebEngineWidgets
import folium
import cv2
import data_capture

DISABLE_DATA_CAPTURE = True
DISABLE_CAMERA = True

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window size and title
        self.setGeometry(0, 0, 1920, 540)
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

        # Set font size for labels
        font = QFont('Arial', 40)
        large_font = QFont('Arial', 60)
        self.speedLabel.setFont(large_font)
        self.distanceLabel.setFont(font)
        self.temperatureLabel.setFont(font)
        self.timeLabel.setFont(font)
        self.batteryLabel.setFont(font)
        self.lapCountLabel.setFont(font)
        self.currentLabel.setFont(font)
        self.PPVoltageLabel.setFont(font)

        # Add labels to layout
        left.addWidget(self.speedLabel, 0, 0)
        left.addWidget(self.distanceLabel, 1, 0)
        left.addWidget(self.timeLabel, 2, 0)
        left.addWidget(self.lapCountLabel, 3, 0)

        left.addWidget(self.batteryLabel, 1, 1)
        left.addWidget(self.temperatureLabel, 2, 1)
        left.addWidget(self.currentLabel, 3, 1)
        left.addWidget(self.PPVoltageLabel, 4, 1)

        # Update time every second
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(20)  # Update every 20 milliseconds

        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self.display_camera_streams)
        self.camera_timer.start(30) # about 30 fps

        self.front_video = None
        self.back_video = None

        if not DISABLE_CAMERA : self.camera_setup()

        if not DISABLE_DATA_CAPTURE:
            self.data_capture = data_capture.DataCapture()

    def camera_setup(self):
        self.front_video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.back_video = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    def display_camera_streams(self):

        if DISABLE_CAMERA: return

        ret1, frame1 = self.front_video.read()
        ret2, frame2 = self.back_video.read()

        if not ret1 or not ret2:
            print("Failed to capture video frames")
            return

        cv2.imshow("Front Camera", frame1)
        cv2.imshow("Back Camera", frame2)

        if cv2.waitKey(1) == ord('q'):
            self.front_video.release()
            self.back_video.release()
            cv2.destroyAllWindows()

    def update_data(self):
        if DISABLE_DATA_CAPTURE: return
        data = self.data_capture.get_data()
        self.speedLabel.setText('Speed: ' + str(data['speed']) + ' km/h')
        self.distanceLabel.setText('Distance: ' + str(data['distance']) + ' km')
        self.temperatureLabel.setText('Temperature: ' + str(data['temperature']) + '°C')
        self.timeLabel.setText('Time: ' + str(data['time']))
        self.batteryLabel.setText('Battery: ' + str(data['battery']) + 'V')
        self.lapCountLabel.setText('Lap Count: ' + str(data['lap']))
        self.currentLabel.setText('Current (I): ' + str(data['I']) + 'A')
        self.PPVoltageLabel.setText('PPV: ' + str(data['PPV']) + 'V')
        self.map = folium.Map(location=data["gps"], zoom_start=15)



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()



    sys.exit(app.exec_())
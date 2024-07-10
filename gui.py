import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QHBoxLayout 
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QFont
from PyQt5 import QtWebEngineWidgets
import folium

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
        self.timeLabel = QLabel('Time: ' + QDateTime.currentDateTime().toString())
        self.batteryLabel = QLabel('Battery: 100%')
        self.lapCountLabel = QLabel('Lap Count: 0')

        # Set font size for labels
        font = QFont('Arial', 40)
        large_font = QFont('Arial', 60)
        self.speedLabel.setFont(large_font)
        self.distanceLabel.setFont(font)
        self.temperatureLabel.setFont(font)
        self.timeLabel.setFont(font)
        self.batteryLabel.setFont(font)
        self.lapCountLabel.setFont(font)

        # Add labels to layout
        left.addWidget(self.speedLabel, 0, 0)
        left.addWidget(self.distanceLabel, 1, 0)
        left.addWidget(self.temperatureLabel, 2, 0)
        left.addWidget(self.timeLabel, 1, 1)
        left.addWidget(self.batteryLabel, 2, 1)
        left.addWidget(self.lapCountLabel, 3, 1)

        # Update time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)  # Update every 1000 milliseconds

    def updateTime(self):
        self.timeLabel.setText('Time: ' + QDateTime.currentDateTime().toString())

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
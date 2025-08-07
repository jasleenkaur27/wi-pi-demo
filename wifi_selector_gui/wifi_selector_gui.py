import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QCheckBox, QScrollArea
)
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt5.QtCore import Qt

class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Wi-Fi Selector")
        self.setStyleSheet("background-color: #1f1f1f; color: white;")
        self.setGeometry(100, 100, 320, 480)

        layout = QVBoxLayout()

        # Header
        header = QLabel("Internet")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        # Toggle Wi-Fi
        toggle_layout = QHBoxLayout()
        self.toggle_wifi = QCheckBox("Use Wi-Fi")
        self.toggle_wifi.setChecked(True)
        self.toggle_wifi.setStyleSheet("QCheckBox { font-size: 14px; }")
        toggle_layout.addWidget(self.toggle_wifi)
        layout.addLayout(toggle_layout)

        # Connected Network Display
        connected_box = QWidget()
        connected_layout = QHBoxLayout()
        connected_box.setLayout(connected_layout)
        connected_box.setStyleSheet("background-color: #3c3f41; padding: 10px; border-radius: 10px;")

        wifi_icon = QLabel()
        wifi_icon.setPixmap(QPixmap("/home/pi/wi-pi-demo/icons/wifi.png").scaled(20, 20))
        connected_layout.addWidget(wifi_icon)

        connected_label = QLabel("eduroam  (Connected)")
        connected_label.setStyleSheet("font-size: 13px;")
        connected_layout.addWidget(connected_label)

        settings_icon = QLabel()
        settings_icon.setPixmap(QPixmap("/home/pi/wi-pi-demo/icons/settings.png").scaled(20, 20))
        settings_icon.setAlignment(Qt.AlignRight)
        connected_layout.addWidget(settings_icon)

        layout.addWidget(connected_box)

        # Networks List
        networks_label = QLabel("Networks")
        networks_label.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(networks_label)

        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2e2e2e; border: none; } QListWidget::item { padding: 10px; }")

        networks = ["ptest", "sait-guest", "sait-mpsk", "CCL-SAIT", "CCL-SAIT_EXT"]
        for network in networks:
            item = QListWidgetItem(QIcon("/home/pi/wi-pi-demo/icons/lock.png"), network)
            self.network_list.addItem(item)

        layout.addWidget(self.network_list)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.show()
    sys.exit(app.exec_())

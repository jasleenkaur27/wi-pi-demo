import sys
import json
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QCheckBox, QScrollArea
)
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt5.QtCore import Qt

def scan_wifi_networks():
    try:
        result = subprocess.run(['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi'], stdout=subprocess.PIPE)
        ssids = set(result.stdout.decode().splitlines())
        return sorted([ssid for ssid in ssids if ssid])
    except Exception as e:
        print(f"Wi-Fi scan failed: {e}")
        return []

class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Wi-Fi Selector")
        self.setStyleSheet("background-color: #1f1f1f; color: white;")
        self.setGeometry(100, 100, 320, 480)

        layout = QVBoxLayout()

        header = QLabel("Select Wi-Fi Network")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2e2e2e; border: none; } QListWidget::item { padding: 10px; }")

        networks = scan_wifi_networks()
        for ssid in networks:
            item = QListWidgetItem(QIcon("/home/pi/wi-pi-demo/icons/lock.png"), ssid)
            self.network_list.addItem(item)

        self.network_list.itemClicked.connect(self.select_network)
        layout.addWidget(self.network_list)
        self.setLayout(layout)

    def select_network(self, item):
        ssid = item.text()
        password = "securepass123"  # Replace with password prompt logic if needed
        with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
            json.dump({"wifi_name": ssid, "wifi_password": password}, f)

        subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.show()
    sys.exit(app.exec_())

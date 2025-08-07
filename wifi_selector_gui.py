import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt

class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Wi-Fi Selector")
        self.setStyleSheet("background-color: #1f1f1f; color: white;")
        self.setGeometry(100, 100, 320, 480)
        self.layout = QVBoxLayout()

        label = QLabel("Select Wi-Fi Network")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(label)

        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2e2e2e; border: none; } QListWidget::item { padding: 10px; }")
        self.network_list.itemClicked.connect(self.select_network)

        self.layout.addWidget(self.network_list)
        self.setLayout(self.layout)
        self.load_networks()

    def load_networks(self):
        try:
            output = subprocess.check_output("nmcli -t -f SSID device wifi list", shell=True)
            ssids = list(set([line.strip() for line in output.decode().split("\n") if line.strip()]))
            for ssid in ssids:
                self.network_list.addItem(QListWidgetItem(ssid))
        except Exception as e:
            print("Failed to scan networks:", e)

    def select_network(self, item):
        selected_ssid = item.text()
        print("Selected:", selected_ssid)

        with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
            json.dump({
                "wifi_name": selected_ssid,
                "wifi_password": "changeme"
            }, f)

        # Launch main_screen.py
        subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])

        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.show()
    sys.exit(app.exec_())

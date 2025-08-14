import sys
import os
import subprocess
import json
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Admin Dashboard")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setGeometry(0, 0, 320, 480)

        self.selected_ssid = None
        self.password_input = ""
        self.secured_networks = {}

        self.layout = QVBoxLayout()

        # Wi-Pi Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("/home/pi/wi-pi-demo/icons/wi-pi-logo.png").scaled(120, 60, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(logo)

        # Header
        header = QLabel("📶 Available Wi-Fi Networks")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(header)

        # Wi-Fi List
        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2b2b2b; border: none; }")
        self.network_list.itemClicked.connect(self.select_network)
        self.layout.addWidget(self.network_list)

        # Placeholder for Connect Button (shown only after password prompt)
        self.connect_button = QPushButton("✅ Connect & Generate QR/NFC")
        self.connect_button.clicked.connect(self.save_and_launch)
        self.connect_button.setStyleSheet("QPushButton { background-color: #004080; font-size: 14px; padding: 10px; }")
        self.connect_button.hide()
        self.layout.addWidget(self.connect_button)

        self.setLayout(self.layout)

        # Start scanning in a thread
        threading.Thread(target=self.scan_networks, daemon=True).start()

    def scan_networks(self):
        result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY', 'device', 'wifi', 'list'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        networks = set()

        for line in output.strip().split('\n'):
            if line:
                parts = line.split(':')
                if len(parts) >= 1:
                    ssid = parts[0].strip()
                    security = parts[1] if len(parts) > 1 else ''
                    if ssid and ssid not in networks:
                        icon = "/home/pi/wi-pi-demo/icons/lock.png" if security else "/home/pi/wi-pi-demo/icons/unlock.png"
                        self.network_list.addItem(QListWidgetItem(QIcon(icon), ssid))
                        self.secured_networks[ssid] = bool(security)
                        networks.add(ssid)

    def select_network(self, item):
        self.selected_ssid = item.text()
        print(f"Selected: {self.selected_ssid}")

        is_secured = self.secured_networks.get(self.selected_ssid, False)
        self.password_input = ""

        if is_secured:
            # Launch matchbox keyboard with full layout
            subprocess.Popen(["matchbox-keyboard", "-s"])

            # Show password dialog with input field
            password_prompt = QWidget()
            password_prompt.setWindowTitle(f"Enter Password for {self.selected_ssid}")
            password_prompt.setStyleSheet("background-color: #1e1e1e; color: white;")
            password_prompt.setGeometry(60, 180, 200, 100)
            layout = QVBoxLayout()

            label = QLabel("Password:")
            label.setFont(QFont("Arial", 10))
            layout.addWidget(label)

            self.password_input_field = QLineEdit()
            self.password_input_field.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.password_input_field)

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(lambda: self.process_password(password_prompt))
            layout.addWidget(ok_button)

            password_prompt.setLayout(layout)
            password_prompt.show()

            self.password_prompt = password_prompt
        else:
            self.save_and_launch()

    def process_password(self, prompt_widget):
        self.password_input = self.password_input_field.text()
        if not self.password_input:
            QMessageBox.warning(self, "Missing Password", "⚠️ Password is required for secured networks.")
            return

        # Close prompt and keyboard
        prompt_widget.close()
        subprocess.call(["pkill", "matchbox-keyboard"])

        # Show connect button now
        self.connect_button.show()

    def save_and_launch(self):
        if not self.selected_ssid:
            print("⚠️ Please select a Wi-Fi network.")
            return

        wifi_data = {
            "wifi_name": self.selected_ssid,
            "wifi_password": self.password_input
        }

        try:
            with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
                json.dump(wifi_data, f)
            print("✅ Network info saved. Launching QR/NFC screen...")
        except Exception as e:
            print(f"Error saving network info: {e}")
            return

        subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.showFullScreen()
    sys.exit(app.exec_())

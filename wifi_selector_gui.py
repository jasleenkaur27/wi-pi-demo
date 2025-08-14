import sys
import os
import subprocess
import json
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox
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

        layout = QVBoxLayout()

        # Wi-Pi Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("/home/pi/wi-pi-demo/icons/wi-pi-logo.png").scaled(120, 60, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Header
        header = QLabel("📶 Available Wi-Fi Networks")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        # Wi-Fi List
        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2b2b2b; border: none; }")
        self.network_list.itemClicked.connect(self.select_network)
        layout.addWidget(self.network_list)

        self.setLayout(layout)

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
        password = ""

        if is_secured:
            keyboard_process = subprocess.Popen(["onboard"])  # Launch on-screen keyboard

            # Use a custom password prompt
            pw_prompt = QWidget()
            pw_prompt.setWindowTitle(f"Enter Password for {self.selected_ssid}")
            pw_prompt.setStyleSheet("background-color: #1e1e1e; color: white;")
            pw_layout = QVBoxLayout()

            label = QLabel(f"Password for {self.selected_ssid}:")
            label.setFont(QFont("Arial", 12))
            pw_layout.addWidget(label)

            pw_input = QLineEdit()
            pw_input.setEchoMode(QLineEdit.Password)
            pw_input.setFont(QFont("Arial", 12))
            pw_input.setStyleSheet("background-color: white; color: black;")
            pw_layout.addWidget(pw_input)

            submit_btn = QPushButton("Generate QR/NFC")
            submit_btn.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-size: 14px;")
            pw_layout.addWidget(submit_btn)

            def on_submit():
                password_val = pw_input.text()
                if not password_val:
                    QMessageBox.warning(self, "Missing Password", "⚠️ Password is required.")
                    return
                self.password_input = password_val
                keyboard_process.terminate()
                pw_prompt.close()
                self.save_and_launch()

            submit_btn.clicked.connect(on_submit)
            pw_prompt.setLayout(pw_layout)
            pw_prompt.show()
        else:
            self.password_input = ""
            self.save_and_launch()

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

        # Launch main_screen.py in background
        subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.showFullScreen()
    sys.exit(app.exec_())

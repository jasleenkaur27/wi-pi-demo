import sys
import os
import subprocess
import json
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QLineEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt


class PasswordPrompt(QDialog):
    def __init__(self, ssid):
        super().__init__()
        self.setWindowTitle(f"Enter Password for {ssid}")
        self.setFixedSize(300, 150)
        self.move(250, 50)  # Place in upper half of screen
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        label = QLabel(f"Password for {ssid}:")
        label.setFont(QFont("Arial", 12))
        layout.addWidget(label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Admin Dashboard")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setGeometry(0, 0, 800, 480)  # Top half of 800x480 screen

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
        # Launch matchbox-keyboard just before password prompt
        kb_proc = subprocess.Popen(["matchbox-keyboard", "-geometry", "800x160+0+320"])

        # Show password prompt
        prompt = PasswordPrompt(self.selected_ssid)
        prompt.password_input.setFocus()
        result = prompt.exec_()

        # Close keyboard after dialog
        kb_proc.terminate()

        if result == QDialog.Accepted:
            password = prompt.password_input.text()
            if not password:
                return
        else:
            return  # Cancelled

    self.password_input = password
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

        # Launch main_screen.py
        subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.show()  # No fullscreen
    sys.exit(app.exec_())

import sys
import os
import subprocess
import json
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QDialog, QLineEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, ssid):
        super().__init__()
        self.setWindowTitle(f"Enter Password for {ssid}")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setFixedSize(300, 120)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)

        layout = QVBoxLayout()
        self.label = QLabel("Password:")
        self.label.setFont(QFont("Arial", 10))
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)

        btn_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_button)
        btn_layout.addWidget(self.ok_button)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Admin Dashboard")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.showFullScreen()

        self.selected_ssid = None
        self.password_input = ""
        self.secured_networks = {}

        layout = QVBoxLayout()

        # Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("/home/pi/wi-pi-demo/icons/wi-pi-logo.png").scaled(120, 60, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Header
        header = QLabel("📶 Available Wi-Fi Networks")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)

        # Network List
        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2b2b2b; border: none; }")
        self.network_list.itemClicked.connect(self.select_network)
        layout.addWidget(self.network_list)

        self.setLayout(layout)

        threading.Thread(target=self.scan_networks, daemon=True).start()

    def scan_networks(self):
        result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY', 'device', 'wifi', 'list'], stdout=subprocess.PIPE)
        output = result.stdout.decode()
        networks = set()

        for line in output.strip().split('\n'):
            if line:
                parts = line.split(':')
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
            # Launch keyboard (ensure it's not already running)
            subprocess.Popen(["matchbox-keyboard"])
            
            # Show dialog
            dialog = PasswordDialog(self.selected_ssid)
            dialog.move(
                int(self.width() / 2 - dialog.width() / 2),
                int(self.height() / 2 - dialog.height() / 2) - 30
            )
            if dialog.exec_() == QDialog.Accepted:
                password = dialog.input.text()
                if not password:
                    print("⚠️ Empty password not allowed.")
                    subprocess.call(["pkill", "matchbox-keyboard"])
                    return
            else:
                subprocess.call(["pkill", "matchbox-keyboard"])
                return

            # Close keyboard
            subprocess.call(["pkill", "matchbox-keyboard"])

        self.password_input = password
        self.save_and_launch()

    def save_and_launch(self):
        wifi_data = {
            "wifi_name": self.selected_ssid,
            "wifi_password": self.password_input
        }

        try:
            with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
                json.dump(wifi_data, f)
            print("✅ Network info saved. Launching QR/NFC...")
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

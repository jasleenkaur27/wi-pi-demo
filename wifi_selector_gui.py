import sys
import subprocess
import json
import threading
import os

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
        # place in upper area so it doesn't overlap keyboard
        self.move(250, 50)
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

        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)


class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Admin Dashboard")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        # Top portion of a typical 800x480 screen; leave space for keyboard
        self.setGeometry(0, 0, 800, 320)

        self.selected_ssid = None
        self.password_input = ""
        self.secured_networks = {}

        layout = QVBoxLayout()

        # Wi-Pi Logo (guard if file missing)
        logo = QLabel()
        logo_path = "/home/pi/wi-pi-demo/icons/wi-pi-logo.png"
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if not pm.isNull():
                logo.setPixmap(pm)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Header
        header = QLabel("📶 Available Wi-Fi Networks")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        # Wi-Fi List
        self.network_list = QListWidget()
        self.network_list.setStyleSheet(
            "QListWidget { background-color: #2b2b2b; border: none; }"
        )
        self.network_list.itemClicked.connect(self.select_network)
        layout.addWidget(self.network_list)

        self.setLayout(layout)

        # Start scanning in a background thread
        threading.Thread(target=self.scan_networks, daemon=True).start()

    def scan_networks(self):
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SECURITY", "device", "wifi", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            output = result.stdout.decode(errors="ignore")
        except Exception as e:
            print(f"nmcli error: {e}")
            return

        seen = set()
        for line in output.strip().split("\n"):
            if not line:
                continue
            parts = line.split(":")
            ssid = parts[0].strip()
            security = parts[1] if len(parts) > 1 else ""
            if not ssid or ssid in seen:
                continue
            seen.add(ssid)
            icon_path = "/home/pi/wi-pi-demo/icons/lock.png" if security else "/home/pi/wi-pi-demo/icons/unlock.png"
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
            # NOTE: UI from a thread usually needs signals; on Pi it often works, but if it flickers we can move to signals later.
            self.network_list.addItem(QListWidgetItem(icon, ssid))
            self.secured_networks[ssid] = bool(security)

    def select_network(self, item):
        self.selected_ssid = item.text()
        print(f"Selected: {self.selected_ssid}")

        is_secured = self.secured_networks.get(self.selected_ssid, False)
        password = ""

        if is_secured:
            # Launch on-screen keyboard at bottom while prompt is open
            kb_proc = subprocess.Popen(["matchbox-keyboard", "-geometry", "800x160+0+320"])
            try:
                prompt = PasswordPrompt(self.selected_ssid)
                prompt.password_input.setFocus()
                result = prompt.exec_()
            finally:
                # Close keyboard after dialog no matter what
                kb_proc.terminate()

            if result == QDialog.Accepted:
                password = prompt.password_input.text().strip()
                if not password:
                    return
            else:
                return  # cancelled

        self.password_input = password
        self.save_and_launch()

    def save_and_launch(self):
        if not self.selected_ssid:
            print("⚠️ Please select a Wi-Fi network.")
            return

        wifi_data = {
            "wifi_name": self.selected_ssid,
            "wifi_password": self.password_input,
        }

        try:
            with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
                json.dump(wifi_data, f)
            print("✅ Network info saved. Launching QR/NFC screen...")
        except Exception as e:
            print(f"Error saving network info: {e}")
            return

        # Launch main_screen.py (expects qrcode / pillow installed)
        subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.show()  # not fullscreen; leaves room for keyboard
    sys.exit(app.exec_())

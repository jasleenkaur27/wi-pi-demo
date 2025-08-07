import sys
import json
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QCheckBox, QInputDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

def scan_wifi_networks():
    try:
        result = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SECURITY', 'dev', 'wifi'], encoding='utf-8')
        networks = []
        for line in result.strip().split('\n'):
            if line:
                parts = line.split(':')
                ssid = parts[0].strip()
                security = parts[1].strip() if len(parts) > 1 else ""
                if ssid and ssid not in [net["ssid"] for net in networks]:
                    networks.append({"ssid": ssid, "secure": bool(security)})
        return networks
    except subprocess.CalledProcessError as e:
        print("Error scanning networks:", e)
        return []

class WifiSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Wi-Fi Selector")
        self.setStyleSheet("background-color: #1f1f1f; color: white;")
        self.setGeometry(100, 100, 320, 480)

        layout = QVBoxLayout()

        # Header
        header = QLabel("Available Networks")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.network_list = QListWidget()
        self.network_list.setStyleSheet("QListWidget { background-color: #2e2e2e; border: none; } QListWidget::item { padding: 10px; }")
        self.network_list.itemClicked.connect(self.select_network)
        layout.addWidget(self.network_list)

        self.setLayout(layout)
        self.load_networks()

    def load_networks(self):
        self.network_list.clear()
        networks = scan_wifi_networks()
        for net in networks:
            icon_path = "/home/pi/wi-pi-demo/icons/lock.png" if net["secure"] else "/home/pi/wi-pi-demo/icons/unlock.png"
            item = QListWidgetItem(QIcon(icon_path), net["ssid"])
            item.setData(Qt.UserRole, net)
            self.network_list.addItem(item)

    def select_network(self, item):
        net = item.data(Qt.UserRole)
        ssid = net["ssid"]
        password = ""

        if net["secure"]:
            password, ok = QInputDialog.getText(self, "Enter Password", f"Enter password for {ssid}:")
            if not ok or not password:
                QMessageBox.warning(self, "Cancelled", "Wi-Fi selection cancelled.")
                return

        # Save to selected_network.json
        try:
            with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
                json.dump({"wifi_name": ssid, "wifi_password": password}, f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save network: {e}")
            return

        # Launch main_screen.py
        try:
            subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch QR screen: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WifiSelector()
    window.show()
    sys.exit(app.exec_())

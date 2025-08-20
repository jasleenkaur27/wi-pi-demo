import sys
import json
import os
import subprocess # Added the missing subprocess import
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import qrcode
from PIL import Image

# Main screen class to display the QR code and other information
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Dashboard")
        self.setGeometry(0, 0, 720, 1250)
        self.setFixedSize(720, 1250)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.setup_ui()

    def setup_ui(self):
        """Sets up the user interface elements."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Main header
        header = QLabel("Scan to Join Wi-Fi")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Spacer
        layout.addSpacing(50)

        # Generate and display QR Code
        wifi_name, wifi_password = self.load_selected_network()
        qr_img = self.generate_qr_image(wifi_name, wifi_password)
        
        qr_label = QLabel()
        # Convert PIL Image to QPixmap
        qr_pixmap = QPixmap.fromImage(qr_img.toqimage())
        # Scale QR code to a larger size, for example 500x500
        scaled_qr = qr_pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qr_label.setPixmap(scaled_qr)
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)

        # Spacer
        layout.addSpacing(50)
        
        # Display the SSID as text
        ssid_label = QLabel(f"Network: {wifi_name}")
        ssid_label.setFont(QFont("Arial", 16))
        ssid_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(ssid_label)

        # Wi-Pi Logo at the bottom that can be double-tapped
        self.logo_label = QLabel()
        logo_path = "/home/pi/wi-pi-demo/icons/wi-pi-logo.png"
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(150, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if not pm.isNull():
                self.logo_label.setPixmap(pm)
        else:
            self.logo_label.setText("Wi-Pi")
            self.logo_label.setFont(QFont("Arial", 24, QFont.Bold))
            
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setToolTip("Double-tap to go to Login")
        # Enable mouse events for the logo label
        self.logo_label.mouseDoubleClickEvent = self.go_to_login
        layout.addWidget(self.logo_label)

        self.setLayout(layout)

    def load_selected_network(self):
        """Loads Wi-Fi network information from a JSON file."""
        try:
            with open("/home/pi/wi-pi-demo/selected_network.json", "r") as f:
                data = json.load(f)
                return data["wifi_name"], data["wifi_password"]
        except Exception as e:
            print(f"Error loading selected network: {e}")
            return "WiPi_Network", "securepass123"

    def generate_qr_image(self, ssid, password):
        """Generates a QR code image from the Wi-Fi data."""
        qr_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        return qr.make_image(fill="black", back_color="white")

    def go_to_login(self, event):
        """
        Handles double-click event on the logo to go to a login page.
        """
        print("Double-tapped on Wi-Pi logo. Navigating to login page...")
        try:
            subprocess.Popen(["python3", "/home/pi/wi-pi-demo/login_screen.py"])
            self.close()
        except FileNotFoundError:
            print("Error: login_screen.py not found. Please ensure the path is correct.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainScreen()
    window.show()
    sys.exit(app.exec_())

import sys
import subprocess
import json
import threading
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QLineEdit, QHBoxLayout,
    QStackedWidget,
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

# This class represents the password input dialog box.
class PasswordPrompt(QDialog):
    def __init__(self, ssid):
        super().__init__()
        self.setWindowTitle(f"Enter Password for {ssid}")
        self.setFixedSize(300, 150)
        # Place in upper area so it doesn't overlap keyboard
        self.move(250, 50)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        # This line is added to make the dialog application modal,
        # preventing it from being closed by clicking outside of it.
        self.setWindowModality(Qt.ApplicationModal)
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
        # Styled the "OK" button to be blue with rounded corners
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 8px 16px;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        # Styled the "Cancel" button with inverted colors and rounded corners
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #007BFF;
                border: 2px solid #007BFF;
                border-radius: 15px;
                padding: 6px 14px;
            }
            QPushButton:pressed {
                background-color: #F0F0F0;
                color: #0056b3;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

    def get_password(self):
        return self.password_input.text().strip()

# This is the main Wi-Fi selection screen, a part of the stacked widget.
class WifiSelectorScreen(QWidget):
    # Signal to emit when a network is selected, with SSID and password.
    network_selected = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.secured_networks = {}
        
        self.setup_ui()
        # Start scanning in a background thread
        threading.Thread(target=self.scan_networks, daemon=True).start()

    def setup_ui(self):
        """Sets up the user interface elements."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 40)  # add safe margins all around
        layout.setSpacing(15)  # space between widgets

        # Wi-Pi Logo (guard if file missing)
        logo = QLabel()
        logo_path = "/home/pi/wi-pi-demo/icons/wi-pi-logo.png"
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if not pm.isNull():
                logo.setPixmap(pm)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Header with a better sign/design
        header = QLabel(" Available Wi-Fi Networks")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        # Wi-Fi List
        self.network_list = QListWidget()
        self.network_list.setStyleSheet(
            "QListWidget { background-color: #2b2b2b; border: 2px solid #3d3d3d; border-radius: 10px; padding: 5px; }"
            "QListWidget::item { background-color: #2b2b2b; color: white; padding: 8px; border-bottom: 1px solid #3d3d3d; }"
            "QListWidget::item:selected { background-color: #007BFF; }"
        )
        self.network_list.itemClicked.connect(self.select_network)
        layout.addWidget(self.network_list)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setFont(QFont("Arial", 14, QFont.Bold))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 10px;
                border: none;
                border-radius: 20px;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """)
        refresh_button.setFixedHeight(50) 
        refresh_button.clicked.connect(lambda: threading.Thread(target=self.scan_networks, daemon=True).start())
        layout.addWidget(refresh_button)

        self.setLayout(layout)

    def scan_networks(self):
        """
        Scans for Wi-Fi networks using the `nmcli` command and populates the list.
        """
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SECURITY", "device", "wifi", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
            )
            output = result.stdout.decode(errors="ignore")
        except Exception as e:
            print(f"nmcli error: {e}")
            self.network_list.clear()
            self.network_list.addItem("Error scanning for networks.")
            return

        self.secured_networks.clear()
        self.network_list.clear()
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
            
            # Use the original icon logic
            lock_icon_path = "/home/pi/wi-pi-demo/icons/lock.png"
            unlock_icon_path = "/home/pi/wi-pi-demo/icons/unlock.png"
            icon_path = lock_icon_path if security else unlock_icon_path
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
            
            item = QListWidgetItem(icon, ssid)
            self.network_list.addItem(item)
            self.secured_networks[ssid] = bool(security)

    def select_network(self, item):
        """
        Handles network selection, prompts for a password if needed,
        and then emits a signal with the data.
        """
        selected_ssid = item.text()
        print(f"Selected: {selected_ssid}")

        is_secured = self.secured_networks.get(selected_ssid, False)
        password = ""

        if is_secured:
            # Launch on-screen keyboard at bottom while prompt is open
            try:
                kb_proc = subprocess.Popen(["matchbox-keyboard", "-geometry", "800x160+0+320"])
            except FileNotFoundError:
                print("matchbox-keyboard not found. Skipping keyboard launch.")
                kb_proc = None

            prompt = PasswordPrompt(selected_ssid)
            prompt.password_input.setFocus()
            result = prompt.exec_()
            
            if kb_proc:
                kb_proc.terminate()

            if result == QDialog.Accepted:
                password = prompt.get_password()
                if not password:
                    return
            else:
                return  # Cancelled

        # Emit signal to trigger the next step in the main manager
        self.network_selected.emit(selected_ssid, password)

# A new screen to show that the next script is launching.
class LaunchScreen(QWidget):
    # Removed the go_back signal as it is no longer needed.
    def __init__(self, ssid, password):
        super().__init__()
        self.ssid = ssid
        self.password = password
        self.setup_ui()
        # Launch the main_screen.py script after a short delay or immediately
        self.save_and_launch()

    def setup_ui(self):
        """Sets up the UI for the launch screen."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        message_label = QLabel(f"Network info for '{self.ssid}' saved.")
        message_label.setFont(QFont("Arial", 16))
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)
        
        launch_label = QLabel("Launching main_screen.py...")
        launch_label.setFont(QFont("Arial", 16, QFont.Bold))
        launch_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(launch_label)

        self.setLayout(layout)

    def save_and_launch(self):
        """Saves network info to a JSON file and launches the main screen."""
        wifi_data = {
            "wifi_name": self.ssid,
            "wifi_password": self.password,
        }
        try:
            with open("/home/pi/wi-pi-demo/selected_network.json", "w") as f:
                json.dump(wifi_data, f)
            print("âœ… Network info saved. Launching main_screen.py...")
        except Exception as e:
            print(f"Error saving network info: {e}")
            return

        # Launch main_screen.py
        try:
            subprocess.Popen(["python3", "/home/pi/wi-pi-demo/main_screen.py"])
        except FileNotFoundError:
            print("Error: main_screen.py not found. Please ensure the path is correct.")

# This class manages the different Wi-Fi screens using a stacked widget.
class WifiManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Pi | Admin Dashboard")
        self.setStyleSheet("background-color: #1e1e1e;")
        self.setGeometry(0, 0, 720, 1250)
        self.setFixedSize(720, 1250)
        
        self.stacked_widget = QStackedWidget()
        self.selector_screen = WifiSelectorScreen()
        
        self.stacked_widget.addWidget(self.selector_screen)
        
        # Connect signals from the selector screen
        self.selector_screen.network_selected.connect(self.show_launch_screen)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def show_launch_screen(self, ssid, password):
        """Creates and displays the launch screen."""
        launch_screen = LaunchScreen(ssid, password)
        
        # Removed the signal connection for the go_back button.
        # launch_screen.go_back.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Add the new screen to the stacked widget and display it
        self.stacked_widget.addWidget(launch_screen)
        self.stacked_widget.setCurrentWidget(launch_screen)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WifiManager()
    window.show()
    sys.exit(app.exec_())

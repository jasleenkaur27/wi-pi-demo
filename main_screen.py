import qrcode
from PIL import Image, ImageTk
import json
import threading
import tkinter as tk
import os
from nfc_writer import write_nfc

# ---------- Load Wi-Fi credentials from selected_network.json ----------
def load_selected_network():
    try:
        with open("selected_network.json", "r") as f:
            data = json.load(f)
            return data["wifi_name"], data["wifi_password"]
    except Exception as e:
        print("⚠️ Error loading selected network:", e)
        return "WiPi_Network", "securepass123"

# ---------- Generate QR Code ----------
def generate_qr_image(ssid, password):
    qr_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    return qr.make_image(fill="black", back_color="white"), qr_data

# ---------- GUI ----------
def launch_gui(qr_img):
    root = tk.Tk()
    root.title("Wi-Pi")
    root.geometry("320x480")
    root.configure(bg='black')

    canvas = tk.Canvas(root, width=320, height=480, bg='black', highlightthickness=0)
    canvas.pack()

    canvas.create_text(160, 30, text="Scan or Tap to Join Wi-Fi", fill="white", font=("Helvetica", 16, "bold"))

    qr_img = qr_img.resize((220, 220))
    qr_img.save("temp_qr.png")
    qr_display = Image.open("temp_qr.png")
    qr_tk = ImageTk.PhotoImage(qr_display)
    canvas.create_image(50, 70, anchor=tk.NW, image=qr_tk)
    root.qr_tk = qr_tk  # Keep reference

    try:
        logo_img = Image.open("wi-pi-logo.png").resize((120, 60))
        logo_tk = ImageTk.PhotoImage(logo_img)
        canvas.create_image(100, 400, anchor=tk.NW, image=logo_tk)
        root.logo_tk = logo_tk
    except Exception as e:
        print("⚠️ Logo not found:", e)
        canvas.create_text(160, 420, text="wi-pi", fill="white", font=("Helvetica", 24, "bold"))

    root.mainloop()

# ---------- Main ----------
if __name__ == "__main__":
    wifi_name, wifi_password = load_selected_network()

    # Generate QR
    qr_img, qr_data = generate_qr_image(wifi_name, wifi_password)

    # Start NFC in background
    threading.Thread(target=write_nfc, args=(qr_data,), daemon=True).start()

    # Show GUI
    launch_gui(qr_img)

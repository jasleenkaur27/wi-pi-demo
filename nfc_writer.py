import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.uart import PN532_UART
import json

# ---------- Read selected network ----------
def read_selected_network():
    try:
        with open("selected_network.json", "r") as f:
            data = json.load(f)
            return data.get("wifi_name", ""), data.get("wifi_password", "")
    except Exception as e:
        print(f"[NFC]  Could not read selected network: {e}")
        return "", ""

# ---------- NFC Writing ----------
def write_nfc():
    print("[NFC] Starting NFC background writer...")
    
    uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=1)
    reset_pin = DigitalInOut(board.D6)
    req_pin = DigitalInOut(board.D12)
    
    pn532 = PN532_UART(uart, debug=False, reset=reset_pin, req=req_pin)
    pn532.SAM_configuration()

    while True:
        print("[NFC] Waiting for NFC tag...")
        uid = pn532.read_passive_target(timeout=5)
        
        if uid is None:
            continue  # No tag detected

        print(f"[NFC] Tag detected with UID: {uid.hex()}")

        ssid, password = read_selected_network()
        if not ssid or not password:
            print("[NFC] Missing SSID or password.")
            continue

        wifi_payload = f"WIFI:T:WPA;S:{ssid};P:{password};;"
        text_bytes = bytearray(wifi_payload, "utf-8")

        try:
            success = pn532.ntag2xx_write_block(4, text_bytes[:4])
            if not success:
                print("[NFC]  Failed to write block 4")
                continue

            print(f"[NFC]  Wi-Fi info written: {ssid}")
            time.sleep(5)  # Pause after successful write

        except Exception as e:
            print(f"[NFC] ⚠️ Exception during write: {e}")
            time.sleep(2)


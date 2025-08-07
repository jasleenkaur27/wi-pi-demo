import nfc
import time
import json

def write_nfc_tag():
    try:
        with open("selected_network.json", "r") as f:
            data = json.load(f)
            ssid = data.get("wifi_name", "")
            password = data.get("wifi_password", "")
    except Exception as e:
        print(f"Failed to load Wi-Fi credentials: {e}")
        return

    wifi_payload = f"WIFI:T:WPA;S:{ssid};P:{password};;"

    clf = nfc.ContactlessFrontend('/dev/ttyS0')  # UART port
    print("Touch NFC tag to write Wi-Fi credentials...")

    def connected(tag):
        try:
            tag.ndef.message = nfc.ndef.Message(nfc.ndef.TextRecord(wifi_payload))
            print(" NFC Tag written successfully!")
        except Exception as e:
            print(f" Failed to write NFC Tag: {e}")
        return True

    clf.connect(rdwr={'on-connect': connected})
    clf.close()

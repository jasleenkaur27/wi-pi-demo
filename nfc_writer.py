import time
import serial
import adafruit_pn532.uart
import ndef
import binascii

# UART connection on /dev/ttyAMA0
uart = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
pn532 = adafruit_pn532.uart.PN532_UART(uart, debug=False)

# Wake up PN532
pn532.SAM_configuration()

print("NFC Writer is ready. Waiting for tag...")

def create_wifi_ndef(ssid, password):
    wifi_payload = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    record = ndef.TextRecord(wifi_payload)
    return [record]

def write_nfc(ssid, password):
    ndef_message = create_wifi_ndef(ssid, password)
    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            print(f"Tag detected: UID={binascii.hexlify(uid)}")
            try:
                print("Writing NDEF to tag...")
                pn532.ndef_write(ndef_message)
                print("✅ NFC tag written successfully!")
                time.sleep(3)
            except Exception as e:
                print("⚠️ Error writing to tag:", e)
                time.sleep(2)

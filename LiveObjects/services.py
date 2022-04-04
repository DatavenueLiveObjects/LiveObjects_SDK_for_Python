#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import time
import sys


def use_existing_network_connection():
    print('Using existing network connection')


def get_mac():
    import uuid
    return ''.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1]).upper()


CONN_TIMEOUT = 20


def wifi_connect(ssid, password):
    from network import WLAN, STA_IF

    sta_if = WLAN(STA_IF)
    sta_if.active(True)
    start_time = time.time()
    while True:
        print('Connecting to network...')
        try:
            sta_if.connect(ssid, password)
            time.sleep_ms(3000)
            if sta_if.isconnected():
                print("WiFi connected successfully.")
                print('Network config:', sta_if.ifconfig())
                break
            elif time.time() - start_time > CONN_TIMEOUT:
                print("[ERROR] Wi-Fi not connected. Stopped.")
                sys.exit()
        except OSError:
            print("[ERROR] Wi-Fi not connected. Stopped.")
            sys.exit()


def get_esp_mac():
    from network import WLAN
    import binascii
    return binascii.hexlify(WLAN().config('mac')).decode('ascii').upper()


def pycom_wifi_connect(ssid, password, hostname):
    from network import WLAN

    wlan = WLAN(mode=WLAN.STA)
    wlan.hostname(hostname)
    start_time = time.time()
    while True:
        print("Trying to connect...")
        wlan.connect(ssid=ssid, auth=(WLAN.WPA2, password))
        time.sleep_ms(3000)
        if wlan.isconnected():
            print("WiFi connected successfully.")
            print('IPs:', wlan.ifconfig(), 'Channel:', wlan.channel())
            break
        elif time.time() - start_time > CONN_TIMEOUT:
            print("[ERROR] Wi-Fi not connected. Stopped.")
            sys.exit()


def get_pycom_mac():
    from network import WLAN
    import binascii
    return binascii.hexlify(WLAN().mac()[0]).decode('ascii').upper()


def lte_connect(pin):
    from network import LTE

    def is_sim_waiting_for_pin():
        if lte.send_at_cmd('AT+CPIN?').strip() == '+CPIN: SIM PIN\r\n\r\nOK':
            return True
        else:
            return False

    lte = LTE()
    time.sleep(2)

    if is_sim_waiting_for_pin():
        print("PIN", (lte.send_at_cmd('AT+CPIN="%s"' % pin)).strip())
    else:
        print("PIN PRESENT: OK")

    lte.attach()
    print("Attaching... ", end='')
    while not lte.isattached():
        time.sleep(1)
    print("attached!")

    lte.connect()
    print("Connecting... ", end='')
    while not lte.isconnected():
        time.sleep(1)
    print("connected!")


def get_pycom_imei():
    from network import LTE
    return LTE().imei()

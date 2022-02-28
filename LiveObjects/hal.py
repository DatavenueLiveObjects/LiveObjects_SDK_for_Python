#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import os
import time

import LiveObjects


class BoardsInterface:

    @staticmethod
    def create_credentials(mode):
        return LiveObjects.Credentials(mode)

    def get_apikey(self):
        return self._credentials.get_apikey()

    def get_client_id(self):
        return self._lang + 'MQTT'

    def mqtt_lib_import_str(self, lang):
        # https://stackoverflow.com/questions/8718885/import-module-from-string-variable
        import_strings = {
            'microPython': 'from umqttrobust import MQTTClient',
            'Python': 'import paho.mqtt.client as paho'
        }
        return import_strings[lang]

    def get_security_level(self):
        return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE

    def network_connect(self):
        pass

    def network_disconnect(self):
        pass


class LoPy(BoardsInterface):
    pass


class GPy(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = True
        self._lte_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(LiveObjects.Credentials.WIFI)

    def network_connect(self):
        pycom_wifi_connect(self._credentials.get_wifi_creds()['ssid'], self._credentials.get_wifi_creds()['password'])


class Esp8266(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = False
        self._wifi_lte_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(LiveObjects.Credentials.WIFI)

    def network_connect(self):
        wifi_connect(self._credentials.get_wifi_creds()['ssid'], self._credentials.get_wifi_creds()['password'])


class Win32(BoardsInterface):
    pass


class Esp32(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = True
        self._wifi_lte_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(LiveObjects.Credentials.WIFI)

    def network_connect(self):
        wifi_connect(self._credentials.get_wifi_creds()['ssid'], self._credentials.get_wifi_creds()['password'])


class Linux(BoardsInterface):
    def __init__(self):
        self._lang = 'Python'
        self._wifi_tls_capability = True
        self._wifi_lte_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(LiveObjects.Credentials.NONE)

    def network_connect(self):
        use_existing_network_connection()


class BoardsFactory:

    def __new__(cls):
        s = os.uname().sysname
        sn = s[0].upper() + s[1:]  # capitalize first letter
        board = eval(sn)()  # instance of board
        return board


def use_existing_network_connection():
    print('Using existing network connection')


def wifi_connect(ssid, password):
    import network

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    while not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.connect(ssid, password)
        if sta_if.isconnected():
            break
        time.sleep(2)
    print('Network config:', sta_if.ifconfig())


CONN_TIMEOUT = 20


def pycom_wifi_connect(ssid, password):
    from network import WLAN

    wlan = WLAN(mode=WLAN.STA)
    wlan.hostname('xPy_1')
    start_time = time.time()
    while 1:
        print("Trying to connect...")
        wlan.connect(ssid=ssid, auth=(WLAN.WPA2, password))
        time.sleep_ms(3000)
        if wlan.isconnected():
            print("WiFi connected succesfully")
            print('IPs:', wlan.ifconfig(), 'Channel:', wlan.channel())
            break
        elif time.time() - start_time > CONN_TIMEOUT:
            print("WiFi not connected. Stopped.")
            break


def mobile_connect(pin):
    # noinspection PyUnresolvedReferences
    from network import LTE
    import socket

    lte = LTE()
    time.sleep(2)
    print("PIN", (lte.send_at_cmd(f'AT+CPIN="{pin}"')).strip())

    lte.attach()
    print("attaching... ", end='')
    while not lte.isattached():
        time.sleep(1)
    print("attached!")

    lte.connect()
    print("connecting... ", end='')
    while not lte.isconnected():
        time.sleep(1)
    print("connected!")

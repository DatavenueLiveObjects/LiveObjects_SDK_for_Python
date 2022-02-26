#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import os
import time


class BoardsInterface:

    def mqtt_lib_import_str(self, lang):
        # https://stackoverflow.com/questions/8718885/import-module-from-string-variable
        import_strings = {
            'microPython': 'from umqttrobust import MQTTClient',
            'Python': 'import paho.mqtt.client as paho'
        }
        return import_strings[lang]

    def network_connect(self, creds):
        pass

    def network_disconnect(self):
        pass


class LoPy(BoardsInterface):
    pass


class GPy(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = True
        self._mobile_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)

    def network_connect(self, creds):
        pass


class Esp8266(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)

    def network_connect(self, creds):
        pass


class Win32(BoardsInterface):
    pass


class Esp32(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)

    def network_connect(self, creds):
        wifi_connect(creds)


class Linux(BoardsInterface):
    def __init__(self):
        self._lang = 'Python'
        self._wifi_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)

    def network_connect(self, creds):
        use_existing_network_connection()


class BoardsFactory:

    def __new__(cls):
        s = os.uname().sysname
        sn = s[0].upper() + s[1:]  # capitalize first letter
        board = eval(sn)()  # instance of board
        return board


def use_existing_network_connection():
    print('Using existing network connection')


def wifi_connect(creds):
    import network

    creds = {'ssid': 'EdekAD57BA', 'pass': 'JANECZEK2000'}
    print('444444444444444444444444444')
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(creds['ssid'], creds['pass'])
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

    # # ------------------ PyCom --------------------------
    # def pycomConn(self):
    #     wlan = WLAN(mode=WLAN.STA)#, bandwidth=WLAN.HT20)
    #     wlan.hostname('xPy_1')
    #     startTime = time.time()
    #     while 1:
    #         print("Trying to connect...")
    #         wlan.connect(ssid='EdekAD57BA', auth=(WLAN.WPA2, 'JANECZEK2000'))
    #         time.sleep_ms(3000)
    #         if wlan.isconnected():
    #             print("WiFi connected succesfully")
    #             print('IPs:', wlan.ifconfig(), 'Channel:', wlan.channel())
    #             break
    #         elif time.time() - startTime > CONN_TIMEOUT:
    #             print("WiFi not connected. Stopped.")
    #             break


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

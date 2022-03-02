#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import os
import time

import LiveObjects


class BoardsInterface:

    DEFAULT_CARRIER = 1
    EXISTING_NETWORK = 2
    WIFI = 3
    LTE = 4

    @staticmethod
    def create_credentials(net_type):
        return LiveObjects.Credentials(net_type)

    def get_apikey(self):
        return self._credentials.get_apikey()

    def get_client_id(self):
        return self._lang + 'MQTT'

    @staticmethod
    def mqtt_lib_import_str(lang):
        import_strings = {
            'microPython': 'from umqttrobust import MQTTClient',
            'Python': 'import paho.mqtt.client as paho'
        }
        return import_strings[lang]

    def get_security_level(self):
        pass

    def network_connect(self):
        pass

    def network_disconnect(self):
        pass


class LoPy(BoardsInterface):
    pass


class GPy(BoardsInterface):
    def __init__(self, net_type):
        self._lang = 'microPython'
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._wifi_tls_capability = True
        self._lte_tls_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(self._net_type)

    def network_connect(self):
        if self._net_type == BoardsInterface.WIFI:
            pycom_wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'])
        elif self._net_type == BoardsInterface.LTE:
            lte_connect(self._credentials.get_creds()['pin'])

    def get_security_level(self):
        if self._net_type == BoardsInterface.WIFI:
            return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE
        elif self._net_type == BoardsInterface.LTE:
            return LiveObjects.SSL if self._lte_tls_capability else LiveObjects.NONE


class Esp8266(BoardsInterface):
    def __init__(self, net_type):
        self._lang = 'microPython'
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else None
        self._wifi_tls_capability = False
        self._wifi_lte_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(BoardsInterface.WIFI)

    def network_connect(self):
        if self._net_type == BoardsInterface.WIFI:
            wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'])

    def get_security_level(self):
        if self._net_type == BoardsInterface.WIFI:
            return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE


class Win32(BoardsInterface):
    pass


class Esp32(BoardsInterface):
    def __init__(self, net_type):
        self._lang = 'microPython'
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else None
        self._wifi_tls_capability = True
        self._wifi_lte_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(BoardsInterface.WIFI)

    def network_connect(self):
        if self._net_type == BoardsInterface.WIFI:
            wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'])

    def get_security_level(self):
        if self._net_type == BoardsInterface.WIFI:
            return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE


class Linux(BoardsInterface):
    def __init__(self, net_type):
        self._lang = 'Python'
        self._net_type = BoardsInterface.EXISTING_NETWORK if net_type == BoardsInterface.DEFAULT_CARRIER else None
        self._wifi_tls_capability = True
        self._wifi_lte_capability = False
        self._mqtt_lib = super().mqtt_lib_import_str(self._lang)
        self._credentials = super().create_credentials(self._net_type)

    def network_connect(self):
        if self._net_type == BoardsInterface.EXISTING_NETWORK:
            use_existing_network_connection()

    def get_security_level(self):
        if self._net_type == BoardsInterface.EXISTING_NETWORK:
            return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE


class BoardsFactory:

    def __new__(cls, net_type):
        s = os.uname().sysname
        sn = s[0].upper() + s[1:]  # capitalize first letter
        board = eval(sn)(net_type)  # instance of board w/ net type: WiFi, LTE, etc.
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


# noinspection PyUnresolvedReferences
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


# noinspection PyUnresolvedReferences
def lte_connect(pin):

    from network import LTE

    lte = LTE()
    time.sleep(2)
    print("PIN", (lte.send_at_cmd('AT+CPIN="%s"' % pin)).strip())

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

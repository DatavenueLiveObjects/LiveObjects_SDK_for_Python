#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import os
from LiveObjects.credentials import Credentials, WIFI, MOBILE


class BoardsInterface:
    credentials = Credentials().get_credentials()

    def mqtt_lib_import(self, lang):
        # https://stackoverflow.com/questions/8718885/import-module-from-string-variable
        import_strings = {
            'microPython': 'from umqttrobust import MQTTClient',
            'Python': 'import paho.mqtt.client as paho'
        }
        return import_strings[lang]


class LoPy(BoardsInterface):
    pass


class GPy(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = True
        self._mobile_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import(self._lang)


class Esp8266(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = False
        self._mqtt_lib = super().mqtt_lib_import(self._lang)


class Win32(BoardsInterface):
    pass


class Esp32(BoardsInterface):
    def __init__(self):
        self._lang = 'microPython'
        self._wifi_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import(self._lang)


class Linux(BoardsInterface):
    def __init__(self):
        self._lang = 'Python'
        self._wifi_tls_capability = True
        self._mqtt_lib = super().mqtt_lib_import(self._lang)


class BoardsFactory:

    def __new__(cls):
        sn = os.uname().sysname
        sn_u = sn[0].upper() + sn[1:]   # first letter upper
        board = eval(sn_u)()            # instance of board
        return board

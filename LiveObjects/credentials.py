#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution
import LiveObjects


class Credentials:

    def __init__(self, net_type):
        self._apikey = <APIKEY>

        if net_type == LiveObjects.BoardsInterface.WIFI:
            self._wifi_ssid = <WIFI_SSID>
            self._wifi_password = <WIFI PASS>
        elif net_type == LiveObjects.BoardsInterface.LTE:
            self._pin = <PIN>
            self._apn = <APN_NAME>

    def get_apikey(self):
        return self._apikey

    def get_wifi_creds(self):
        return {'ssid': self._wifi_ssid, 'password': self._wifi_password}

    def get_lte_creds(self):
        return self._pin, self._apn

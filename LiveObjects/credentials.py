#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution
class Credentials:

    NONE = 1
    WIFI = 2
    LTE = 3

    def __init__(self, net_type=NONE):
        self._apikey = <APIKEY>

        if net_type == Credentials.WIFI:
            self._wifi_ssid = <WIFI_SSID>
            self._wifi_password = <WIFI PASS>
        elif net_type == Credentials.LTE:
            self._pin = <PIN>
            self._apn = <APN_NAME>

    def get_apikey(self):
        return self._apikey

    def get_wifi_creds(self):
        return {'ssid': self._wifi_ssid, 'password': self._wifi_password}

    def get_lte_creds(self):
        return self._pin, self._apn

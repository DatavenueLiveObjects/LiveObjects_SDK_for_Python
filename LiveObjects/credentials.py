#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

NONE = 1
WIFI = 2
LTE = 3


class Credentials:
    def __init__(self, net_type=NONE):
        self._apikey = '0ce12ecdd74343bd9360b63888033de0'

        if net_type == WIFI:
            self._wifi_ssid = 'EdekAD57BA'
            self._wifi_password = 'JANECZEK2000'
        elif net_type == LTE:
            self._pin = '1155'
            self._apn = 'internet'

    def get_apikey(self):
        return self._apikey

    def get_wifi_creds(self):
        return {'ssid': self._wifi_ssid, 'pass': self._wifi_password}

    def get_lte_creds(self):
        return self._pin, self._apn

#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution
import LiveObjects


class Credentials:

    def __init__(self, net_type):

        self._apikey = '<APIKEY>'
        self._net_type = net_type

        if net_type == LiveObjects.BoardsInterface.WIFI:
            self._wifi_ssid = '<WIFI_SSID>'
            self._wifi_password = '<WIFI_PASS>'
        elif net_type == LiveObjects.BoardsInterface.LTE:
            self._pin = '<PIN>'
            self._apn = '<APN>'

    def get_apikey(self):
        return self._apikey

    def get_creds(self):
        if self._net_type == LiveObjects.BoardsInterface.WIFI:
            return {'ssid': self._wifi_ssid, 'password': self._wifi_password}
        elif self._net_type == LiveObjects.BoardsInterface.LTE:
            return {'pin': self._pin, 'apn_name': self._apn}

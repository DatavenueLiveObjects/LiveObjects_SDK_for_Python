#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

NONE = 1
WIFI = 2
MOBILE = 3


class Credentials:
    def __init__(self, net_type=NONE):
        self._lo_id = '0ce12ecdd74343bd9360b63888033de0'

        if net_type == WIFI:
            self._wifi_ssid = 'EdekAD57BA'
            self._wifi_password = 'JANECZEK2000'
        elif net_type == MOBILE:
            self._pin = '1155'
            self._apn = 'internet'

    def get_credentials(self):
        return self

    def get_lo_id(self):
        return self._lo_id

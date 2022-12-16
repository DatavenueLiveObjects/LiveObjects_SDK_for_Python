#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import sys
import LiveObjects


class BoardsInterface:

    DEFAULT_CARRIER = 1
    EXISTING_NETWORK = 2
    WIFI = 3
    LTE = 4

    PYTHON = 1
    MICROPYTHON = 2

    @staticmethod
    def create_credentials(net_type):
        return LiveObjects.Credentials(net_type)

    def get_apikey(self):
        return self._credentials.get_apikey()

    def get_client_id(self):
        pass

    def get_lang_str(self):
        lang_dict = {BoardsInterface.PYTHON: 'urn:lo:nsid:Python',
                     BoardsInterface.MICROPYTHON: 'urn:lo:nsid:microPython'}
        return lang_dict[self._lang_id]

    def get_lang_id(self):
        return self._lang_id

    def get_security_level(self):
        pass

    def get_store_cert_filename(self):
        pass

    def check_network_capabilities(self, net_type):
        if net_type not in self._carrier_capability:
            print('Carrier not supported.')
            sys.exit()

    def connect(self):
        pass

    def network_disconnect(self):
        pass


class LoPy(BoardsInterface):
    def __init__(self, net_type):
        self._lang_id = BoardsInterface.MICROPYTHON
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._carrier_capability = (BoardsInterface.WIFI,)
        self._wifi_tls_capability = False
        self._credentials = super().create_credentials(self._net_type)
        self._hostname = 'LoPy'

    def connect(self):
        super().check_network_capabilities(self._net_type)
        if self._net_type == BoardsInterface.WIFI:
            from LiveObjects.services import pycom_wifi_connect
            pycom_wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'],
                               self._hostname)

    def get_security_level(self):
        if self._net_type == BoardsInterface.WIFI:
            return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE

    def get_client_id(self):
        from LiveObjects.services import get_pycom_mac
        return self.get_lang_str() + ':' + get_pycom_mac()


class GPy(BoardsInterface):
    def __init__(self, net_type):
        self._lang_id = BoardsInterface.MICROPYTHON
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._carrier_capability = (BoardsInterface.WIFI, BoardsInterface.LTE)
        self._wifi_tls_capability = False
        self._lte_tls_capability = False
        self._credentials = super().create_credentials(self._net_type)
        self._hostname = 'GPy'

    def connect(self):
        super().check_network_capabilities(self._net_type)
        if self._net_type == BoardsInterface.WIFI:
            from LiveObjects.services import pycom_wifi_connect
            pycom_wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'],
                               self._hostname)
        elif self._net_type == BoardsInterface.LTE:
            from LiveObjects.services import lte_connect
            lte_connect(self._credentials.get_creds()['pin'])

    def get_security_level(self):
        if self._net_type == BoardsInterface.WIFI:
            return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE
        elif self._net_type == BoardsInterface.LTE:
            return LiveObjects.SSL if self._lte_tls_capability else LiveObjects.NONE

    def get_client_id(self):
        if self._net_type == BoardsInterface.WIFI:
            from LiveObjects.services import get_pycom_mac
            return self.get_lang_str() + ':' + get_pycom_mac()
        elif self._net_type == BoardsInterface.LTE:
            from LiveObjects.services import get_pycom_imei
            return self.get_lang_str() + ':' + get_pycom_imei()


class Esp8266(BoardsInterface):
    def __init__(self, net_type):
        self._lang_id = BoardsInterface.MICROPYTHON
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._carrier_capability = (BoardsInterface.WIFI,)
        self._wifi_tls_capability = False
        self._credentials = super().create_credentials(self._net_type)

    def connect(self):
        from LiveObjects.services import wifi_connect
        super().check_network_capabilities(self._net_type)
        wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'])

    def get_security_level(self):
        return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE

    def get_client_id(self):
        from LiveObjects.services import get_esp_mac
        return self.get_lang_str() + ':' + get_esp_mac()


class Win32(BoardsInterface):
    def __init__(self, net_type):
        self._lang_id = BoardsInterface.PYTHON
        self._net_type = BoardsInterface.EXISTING_NETWORK if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._carrier_capability = (BoardsInterface.EXISTING_NETWORK,)
        self._existing_network_tls_capability = True
        self._credentials = super().create_credentials(self._net_type)

    def connect(self):
        from LiveObjects.services import use_existing_network_connection
        super().check_network_capabilities(self._net_type)
        use_existing_network_connection()

    def get_security_level(self):
        return LiveObjects.SSL if self._existing_network_tls_capability else LiveObjects.NONE

    def get_store_cert_filename(self):
        try:
            import certifi
            return certifi.where()
        except ImportError:
            print("[ERROR] U have missing library 'python-certifi-win32'")
            sys.exit()

    def get_client_id(self):
        from LiveObjects.services import get_mac
        return self.get_lang_str() + ':' + get_mac()


class Esp32(BoardsInterface):
    def __init__(self, net_type):
        self._lang_id = BoardsInterface.MICROPYTHON
        self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._carrier_capability = (BoardsInterface.WIFI,)
        self._wifi_tls_capability = True
        self._credentials = super().create_credentials(self._net_type)

    def connect(self):
        from LiveObjects.services import wifi_connect
        super().check_network_capabilities(self._net_type)
        wifi_connect(self._credentials.get_creds()['ssid'], self._credentials.get_creds()['password'])

    def get_security_level(self):
        return LiveObjects.SSL if self._wifi_tls_capability else LiveObjects.NONE

    def get_client_id(self):
        from LiveObjects.services import get_esp_mac
        return self.get_lang_str() + ':' + get_esp_mac()


class Linux(BoardsInterface):
    def __init__(self, net_type):
        self._lang_id = BoardsInterface.PYTHON
        self._net_type = BoardsInterface.EXISTING_NETWORK if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
        self._carrier_capability = (BoardsInterface.EXISTING_NETWORK,)
        self._existing_network_tls_capability = True
        self._credentials = super().create_credentials(self._net_type)
        self._cert_store_filename = "/etc/ssl/certs/ca-certificates.crt"

    def connect(self):
        from LiveObjects.services import use_existing_network_connection
        super().check_network_capabilities(self._net_type)
        use_existing_network_connection()

    def get_security_level(self):
        return LiveObjects.SSL if self._existing_network_tls_capability else LiveObjects.NONE

    def get_store_cert_filename(self):
        return self._cert_store_filename

    def get_client_id(self):
        from LiveObjects.services import get_mac
        return self.get_lang_str() + ':' + get_mac()


class RaspberryPi(Linux):
    pass


def is_raspberrypi():
    try:
        with open('/proc/device-tree/model') as f:
            return f.read().startswith('Raspberry')
    except FileNotFoundError:
        return False


class BoardsFactory:
    def __new__(cls, net_type):
        s = sys.platform
        sn = s[0].upper() + s[1:]   # capitalize first letter
        if sn == 'Linux':
            sn = 'RaspberryPi' if is_raspberrypi() else 'Linux'
        board = eval(sn)(net_type)  # instance of board w/ net type: WiFi, LTE, etc.
        return board


MAX_DEV_NB = 20


def get_i2c():
    import machine
    typical_gpio = ([22, 23], [5, 4], [22, 21])
    for gpio in typical_gpio:
        scl, sda = gpio
        i2c = None
        try:                    # MicroPython 1.19.1 20220618-v1.19.1
            i2c = machine.SoftI2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000)
            if i2c.scan() and len(i2c.scan()) < MAX_DEV_NB:
                return i2c
        except ValueError:      # next sda, scl
            pass
        except AttributeError:  # Pycom MicroPython 1.20.2.r6 [v1.11-c5a0a97] on 2021-10-28
            i2c = machine.I2C(0)
            return i2c
        del i2c
    raise RuntimeError("No I2C devices found. Check SDA and SCL lines and add respective GPIO to 'typical_gpio'.")


class SensorVL6180X:
    def __new__(cls):
        try:                # Python@RPi
            import busio
            import adafruit_vl6180x
            import board

            class VL6180X(adafruit_vl6180x.VL6180X):
                def amb_light(self):
                    """Implementing default gain"""
                    return self.read_lux(gain=0x06)     # ALS_GAIN_1

            i2c = busio.I2C(board.SCL, board.SDA)
            return VL6180X(i2c)

        except ImportError:  # microPython
            import vl6180x_micro
            i2c = get_i2c()
            return vl6180x_micro.Sensor(i2c)

        except NotImplementedError:  # if no I2C device
            print("No GPIO present.")
            sys.exit()

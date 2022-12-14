#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution
#
#  This file incorporates work covered by the following copyright and
#  permission notice:
#
#  Copyright (c) 2018, Ledbelly2142
#  https://github.com/Ledbelly2142/VL6180X/blob/master/LICENSE
#
#  Copyright (c) 2022, Adafruit
#  https://github.com/adafruit/Adafruit_CircuitPython_VL6180X/blob/main/LICENSE

import ustruct
import struct
import time
from machine import I2C


class Sensor:
    """
    VL6180X sensor measuring distance and ambient light
    """
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self._address = address
        self.default_settings()
        self.init()

    def i2c_write(self, register, regValue):
        return self.i2c.writeto_mem(self._address, register, bytearray([regValue]), addrsize=16), 'big'

    def i2c_read(self, register, nb_bytes=1):
        value = int.from_bytes(
            self.i2c.readfrom_mem(self._address, register, nb_bytes, addrsize=16),
            'big'
        )
        return value & 0xFFFF

    def init(self):
        if self.i2c_read(0x0016) != 1:
            raise RuntimeError("Failure reset")

        # Recommended setup from the datasheet
     
        self.i2c_write(0x0207, 0x01)
        self.i2c_write(0x0208, 0x01)
        self.i2c_write(0x0096, 0x00)
        self.i2c_write(0x0097, 0xfd)
        self.i2c_write(0x00e3, 0x00)
        self.i2c_write(0x00e4, 0x04)
        self.i2c_write(0x00e5, 0x02)
        self.i2c_write(0x00e6, 0x01)
        self.i2c_write(0x00e7, 0x03)
        self.i2c_write(0x00f5, 0x02)
        self.i2c_write(0x00d9, 0x05)
        self.i2c_write(0x00db, 0xce)
        self.i2c_write(0x00dc, 0x03)
        self.i2c_write(0x00dd, 0xf8)
        self.i2c_write(0x009f, 0x00)
        self.i2c_write(0x00a3, 0x3c)
        self.i2c_write(0x00b7, 0x00)
        self.i2c_write(0x00bb, 0x3c)
        self.i2c_write(0x00b2, 0x09)
        self.i2c_write(0x00ca, 0x09)
        self.i2c_write(0x0198, 0x01)
        self.i2c_write(0x01b0, 0x17)
        self.i2c_write(0x01ad, 0x00)
        self.i2c_write(0x00ff, 0x05)
        self.i2c_write(0x0100, 0x05)
        self.i2c_write(0x0199, 0x05)
        self.i2c_write(0x01a6, 0x1b)
        self.i2c_write(0x01ac, 0x3e)
        self.i2c_write(0x01a7, 0x1f)
        self.i2c_write(0x0030, 0x00)

    def default_settings(self):
        # Enables polling for ‘New Sample ready’ when measurement completes
        self.i2c_write(0x0011, 0x10)
        self.i2c_write(0x010A, 0x30)  # Set Avg sample period
        self.i2c_write(0x003f, 0x46)  # Set the ALS gain
        self.i2c_write(0x0031, 0xFF)  # Set auto calibration period
        # (Max = 255)/(OFF = 0)
        self.i2c_write(0x0040, 0x63)  # Set ALS integration time to 100ms
        # perform a single temperature calibration
        self.i2c_write(0x002E, 0x01)

        # Optional settings from datasheet
        self.i2c_write(0x001B, 0x09)  # Set default ranging inter-measurement
        # period to 100ms
        self.i2c_write(0x003E, 0x0A)  # Set default ALS inter-measurement
        # period to 100ms
        self.i2c_write(0x0014, 0x24)  # Configures interrupt on ‘New Sample
        # Ready threshold event’

        # Additional settings defaults from community
        self.i2c_write(0x001C, 0x32)  # Max convergence time
        self.i2c_write(0x002D, 0x10 | 0x01)  # Range check enables
        self.i2c_write(0x0022, 0x7B)  # Eraly coinvergence estimate
        self.i2c_write(0x0120, 0x01)  # Firmware result scaler

    def _range(self):
        """Measure the distance in millimeters. Takes 0.01s."""
        self.i2c_write(0x0018, 0x01)  # Sysrange start
        time.sleep(0.01)
        return self.i2c_read(0x0062)  # Result range value import ustruct

    @property
    def range(self):
        return self._range()

    def read_lux(self, gain=0x06):
        """Read the lux (light value) from the sensor and return it.  Must
        specify the gain value to use for the lux reading:

        =================  =====
             Setting       Value
        =================  =====
        ``ALS_GAIN_1``     1x
        ``ALS_GAIN_1_25``  1.25x
        ``ALS_GAIN_1_67``  1.67x
        ``ALS_GAIN_2_5``   2.5x
        ``ALS_GAIN_5``     5x
        ``ALS_GAIN_10``    10x
        ``ALS_GAIN_20``    20x
        ``ALS_GAIN_40``    40x
        =================  =====

        :param int gain: The gain value to use
        """

        reg = self.i2c_read(0x0014)
        reg &= ~0x38
        reg |= 0x4 << 3  # IRQ on ALS ready
        self.i2c_write(0x0014, reg)
        # 100 ms integration period
        self.i2c_write(0x0040, 0)
        self.i2c_write(0x0041, 100)
        # analog gain
        gain = min(gain, 0x07)
        self.i2c_write(0x003F, 0x40 | gain)
        # start ALS
        self.i2c_write(0x0038, 1)
        # Poll until "New Sample Ready threshold event" is set
        while (
                (self.i2c_read(0x004F) >> 3) & 0x7
        ) != 4:
            pass
        # read lux!
        lux = self.i2c_read(0x0050, 2)
        # clear interrupt
        self.i2c_write(0x0015, 0x07)
        lux *= 0.32  # calibrated count/lux

        if gain == 0x06:  # ALS_GAIN_1:
            pass
        elif gain == 0x05:  # ALS_GAIN_1_25:
            lux /= 1.25
        elif gain == 0x04:  # ALS_GAIN_1_67:
            lux /= 1.67
        elif gain == 0x03:  # ALS_GAIN_2_5:
            lux /= 2.5
        elif gain == 0x02:  # ALS_GAIN_5:
            lux /= 5
        elif gain == 0x01:  # ALS_GAIN_10:
            lux /= 10
        elif gain == 0x00:  # ALS_GAIN_20:
            lux /= 20
        elif gain == 0x07:  # ALS_GAIN_40:
            lux /= 40
        lux *= 100
        lux /= 100  # integration time in ms
        return lux

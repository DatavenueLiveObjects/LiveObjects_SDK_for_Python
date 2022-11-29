#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution
import sys
import time
import LiveObjects

import busio
import adafruit_vl6180x

try:
    import board
except NotImplementedError:     # if no I2C device
    print("No GPIO present.")
    sys.exit()

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
# Create sensor instance.
sensor = adafruit_vl6180x.VL6180X(i2c)
# You can add an offset to distance measurements here (e.g. calibration)
# Swapping for the following would add a +10 millimeter offset to measurements:
# sensor = adafruit_vl6180x.VL6180X(i2c, offset=10)

# Create LiveObjects
lo = LiveObjects.Connection()

MESSAGE_RATE = 5

# Main program
lo.connect()		                    # Connect to LiveObjects
last = uptime = time.time()

while True:
    if (time.time()) >= last + MESSAGE_RATE:
        # lo.add_to_payload("uptime", int(time.time() - uptime))  # Add value to payload: name - value
        lo.add_to_payload("distance", sensor.range)
        lo.add_to_payload("ambient_light", sensor.read_lux(adafruit_vl6180x.ALS_GAIN_1))
        lo.send_data()  # Sending data to cloud
        last = time.time()
        lo.loop() 						# Check for incoming messages and if connection is still active

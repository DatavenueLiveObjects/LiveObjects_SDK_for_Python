#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import time
import LiveObjects

# Create LiveObjects
lo = LiveObjects.Connection()

MESSAGE_RATE = 5

# Main program
lo.connect()		                    # Connect to LiveObjects
last = uptime = time.time()

while True:
    if (time.time()) >= last + MESSAGE_RATE:
        lo.add_to_payload("uptime", int(time.time() - uptime))  # Add value to payload: name - value
        lo.send_data()  # Sending data to cloud
        last = time.time()
        lo.loop() 						# Check for incoming messages and if connection is still active

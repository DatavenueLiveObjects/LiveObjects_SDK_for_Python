#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution


import time
import LiveObjects


# Create LiveObjects
lo = LiveObjects.Connection()


# Callback for a parameter change
def callback(parameterName, newValue):
    print("Changed value of the parameter " + parameterName + " to " + str(newValue))


# Main program
# Available types:  INT, BINARY, STRING, FLOAT
lo.addParameter("messageRate", 5, LiveObjects.INT, callback)		# Add parameter: Name - Value - Type - Callback
lo.connect()		                                                # Connect to LiveObjects
last = uptime = time.time()

while True:
    if time.time() >= last + lo.getParameter("messageRate"):		# Get the parameter using its name
        lo.addToPayload("uptime", int(time.time() - uptime))		# Add value to payload: name - value
        lo.sendData()		# Sending data to cloud
        last = time.time()
        lo.loop()		    # Check for incoming messages and if connection is still active

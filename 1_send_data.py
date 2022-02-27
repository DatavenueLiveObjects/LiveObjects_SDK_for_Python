#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import time
import LiveObjects

board = LiveObjects.BoardsFactory()

apikey = board.get_apikey()
client_id = board.get_client_id()
security_level = board.get_security_level()

# Create LiveObjects with parameters:  Board - ClientID - Security - APIKEY
lo = LiveObjects.Connection(board, client_id, security_level, apikey)

messageRate = 5

# Main program
board.network_connect()
lo.connect()		# Connect to LiveObjects
last = time.time()
uptime = time.time()

while True:
	if time.time() >= last+messageRate:
		lo.addToPayload("uptime", int(time.time() - uptime))		# Add value to payload: name - value
		lo.sendData()												# Sending data to cloud
		lo.loop() 						# Check for incoming messages and if connection is still active
		last = time.time()

#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import time

import LiveObjects


b = LiveObjects.BoardsFactory()
lo_id = LiveObjects.Credentials().get_lo_id()

#Create LiveObjects with parameters:  ClientID - Security - APIKEY
lo = LiveObjects.Connection("PythonMQTT", LiveObjects.SSL, lo_id)

messageRate = 5

#Main program
lo.connect() #Connect to LiveObjects
last = time.time()
uptime = time.time()
while True:
	if time.time()>=last+messageRate:
		lo.addToPayload("uptime", int(time.time() - uptime) ) #Add value to payload: name - value
		lo.sendData() #Sending data to cloud
		lo.loop() #Check for incoming messages and if connection is still active
		last = time.time()
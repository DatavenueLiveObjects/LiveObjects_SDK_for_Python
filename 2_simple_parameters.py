import os
import sys
import time

import LiveObjects

#Create LiveObjects with parameters:  ClientID - Security - APIKEY
lo = LiveObjects.Connection("PythonMQTT", LiveObjects.NONE, "<APIKEY>")

#Main program
lo.addParameter("messageRate", 5 , LiveObjects.INT) #Add parameter: Name - Value - Type
#Available types:  INT BINARY STRING FLOAT
lo.connect() #Connect to LiveObjects
last = time.time()
uptime = time.time()
while True:
	if time.time()>=last+lo.getParameter("messageRate"):#Get the parameter using its name
		lo.addToPayload("uptime", int(time.time() - uptime) ) #Add value to payload: name - value
		lo.sendData() #Sending data to cloud
		lo.loop() #Check for incoming messages and if connection is still active
		last = time.time()
import os
import sys
import time

from LiveObjectsSDK.Connection import *

#Create LiveObjects with parameters:  ClientID - Port - APIKEY
lo = LiveObjects("PythonMQTT", 1883, "<APIKEY>")

messageRate = 5

#Define command function
def foo(arg={}):
    lo.outputDebug(INFO,"Called function foo")
    return {}

#Main program
lo.addCommand("foo",foo) #Add command to LiveObjects: name - function
lo.connect() #Connect to LiveObjects
last = time.time()
uptime = time.time()
while True:
	if time.time()>=last+messageRate:
		lo.addToPayload("uptime", int(time.time() - uptime) ) #Add value to payload: name - value
		lo.sendData() #Sending data to cloud
		lo.loop() #Check for incoming messages and if connection is still active
		last = time.time()
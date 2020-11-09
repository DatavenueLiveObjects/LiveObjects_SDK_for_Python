import os
import sys
import time
import json
import LiveObjects

#Create LiveObjects with parameters:  ClientID - Security - APIKEY
lo = LiveObjects.Connection("PythonMQTT", LiveObjects.NONE, "<APIKEY>")

messageRate = 5

#Define command function with arguments handling
def foo(args={}):
	lo.outputDebug(LiveObjects.INFO,"Called function foo with args", json.dumps(args))
	counter = 0
	for i in range(args["repetitions"]):
		print("Repetition nr "+str(i))
		counter+=1
	return { "Repeated" : str(counter)+" times"}

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
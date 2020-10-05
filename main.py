import os
import sys
try:
	path = os.environ['_']
	#print(path)
	from LiveObjectsSDK import *
except AttributeError:
	print("Micropython detected!")
	if sys.platform == "linux":
		print("running Python3")
		import os
		os.system("python3 main.py")
		sys.exit()
	else:
		from LiveObjectsSDK import *

import time

lo = LiveObjects("PythonMQTT", 1883, "<api key>")

def foo(arg=""):
    lo.outputDebug(INFO,"Called function with foo argument ", arg)
    return { "blinked" : "5 times"}

lo.addCommand("foo",foo)
lo.addParameter("messageRate",5 , INT)
lo.connect()
last = time.time()
uptime = time.time()
while True:
	if time.time()>=last+lo.getParameter("messageRate"):
		lo.addToPayload("uptime", int(time.time() - uptime) )
		lo.sendData()
		lo.loop()
		last = time.time()

from LiveObjectsSDK import *

lo = LiveObjects("PythonMQTT", 8883, "YOUR API KEY")

uptime = 0
def foo(arg=""):
    lo.outputDebug(Debug.INFO,"Wywolalem funkcje foo z argumentem ", arg)
    return { "blinked" : "5 times"}


if __name__ == '__main__':
    lo.addCommand("foo",foo)
    lo.addParameter("messageRate",5 , Type.INT)
    lo.connect()
    uptime = time.time()
    while True:
        lo.addToPayload("uptime", int(time.time()-uptime))
        lo.sendData()
        time.sleep(lo.getParameter("messageRate"))

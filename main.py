from uLiveObjectsSDK import *

lo = LiveObjects("PythonMQTT", 1883, "Your api key")

uptime = 0
def foo(arg=""):
    lo.outputDebug(INFO,"called function with foo arg ", arg)
    return { "blinked" : "5 times"}

last = time.time()

#esp8266 esp32
# def do_connect():
#     import network
#     sta_if = network.WLAN(network.STA_IF)
#     if not sta_if.isconnected():
#         print('connecting to network...')
#         sta_if.active(True)
#         sta_if.connect('<SSID>', '<PASS>')
#         while not sta_if.isconnected():
#             pass
#     print('network config:', sta_if.ifconfig())


if __name__ == '__main__':
    #do_connect()
    lo.addCommand("foo",foo)
    lo.addParameter("messageRate",5 , INT)
    lo.connect()
    uptime = time.time()
    while True:
        if(time.time()>=last+lo.getParameter("messageRate")):
            lo.addToPayload("uptime", int(time.time()-uptime))
            lo.sendData()
            lo.loop()
            last = time.time()

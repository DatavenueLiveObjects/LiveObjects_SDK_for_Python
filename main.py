from uLiveObjectsSDK import *

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('LIKI', 'Newconnect75')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()
lo = LiveObjects("PythonMQTT", 1883, "YOUR API KEY")

uptime = 0
def foo(arg=""):
    lo.outputDebug(INFO,"Wywolalem funkcje foo z argumentem ", arg)
    return { "blinked" : "5 times"}


if __name__ == '__main__':
    lo.addCommand("foo",foo)
    lo.addParameter("messageRate",5 , INT)
    lo.connect()
    uptime = time.time()
    while True:
        lo.addToPayload("uptime", int(time.time()-uptime))
        lo.sendData()
        lo.loop()
        time.sleep(lo.getParameter("messageRate"))

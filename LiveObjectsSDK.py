mode = 0
try:
    import paho.mqtt.client as paho
    import os
    import datetime
    mode = 1
except ImportError:
    try:
        from umqttsimple import *
        import ssl
    except ImportError:
        print("There are no modules i can use! Install paho.mqtt or umqtt")

import json
import time



INT="i32"
UINT="u32"
BINARY="bin"
STRING="str"
FLOAT="f64"
INFO="INFO"
WARNING = "WARNING"
ERROR = "ERROR"

class LiveObjectsParameter:
    def __init__(self,value,type):
        self.value = value
        self.type = type

class LiveObjects:
    def __init__(self, deviceID, port, apiKey, debug = True):
        self.__port = port
        self.__apiKey = apiKey
        self.__parameters = {}
        self.__server = "liveobjects.orange-business.com"
        self.__topic = "dev/data"
        self.__value = "value"
        self.__payload = {self.__value: {}}
        self.__commands = {}
        self.__doLog = debug

        if mode == 1:
            self.__mqtt = paho.Client(deviceID)
        else:
            self.ssl = port == 8883
            self.__mqtt = MQTTClient(deviceID, self.__server, self.__port, "json+device", self.__apiKey, 0, self.ssl)

    def loop(self):
        if mode == 0:
            self.__mqtt.check_msg()

    def __onMessage(self,client="", userdata="", msg=""):
        if mode == 1:
            if msg.topic == "dev/cfg/upd":
                self.__parameterManager(msg)
            elif msg.topic == "dev/cmd":
                self.__commandManager(msg)
        else:
            if client == b"dev/cfg/upd":
                self.__parameterManager(userdata)
            elif client == b"dev/cmd":
                self.__commandManager(userdata)

    def __onConnect(self,client="", userdata="", flags="", rc=""):
        if mode == 1:
            self.outputDebug(INFO,"Connected!")
            if len(self.__commands)>0:
                self.outputDebug(INFO, "Subscribing commands")
                self.__mqtt.subscribe("dev/cmd")
            if len(self.__parameters)>0:
                self.outputDebug(INFO, "Subscribing parameters")
                self.__mqtt.subscribe("dev/cfg/upd")
                self.__sendConfig()
        else:
            self.outputDebug(INFO, "Connected, sending config")
            if len(self.__commands) > 0:
                self.outputDebug(INFO, "Subscribing commands")
                self.__mqtt.subscribe(b"dev/cmd")
            if len(self.__parameters) > 0:
                self.outputDebug(INFO, "Subscribing parameters")
                self.__mqtt.subscribe(b"dev/cfg/upd")
                self.__sendConfig()


    def connect(self):
        if mode == 1:
            self.__mqtt.username_pw_set("json+device", self.__apiKey)
            self.__mqtt.on_connect = self.__onConnect
            self.__mqtt.on_message = self.__onMessage
            if self.__port == 8883:
                dirname = os.path.dirname(__file__)
                filename = os.path.join(dirname, "./certfile.cer")
                self.__mqtt.tls_set(filename)
            self.__mqtt.connect(self.__server, self.__port, 60)
            self.__mqtt.loop_start()
        else:
            self.__mqtt.set_callback(self.__onMessage)
            self.__mqtt.connect()
            time.sleep(1)
            self.__onConnect()


    def outputDebug(self,info, *args):
        if self.__doLog:
            if mode == 1:
                print("[", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "]", end="", sep="")
                print("[",info,"]", end=" ", sep="")
                for arg in args:
                    print(arg, end=" ")
                print("")
            else:
                print("[", info, "]", end=" ", sep="")
                for arg in args:
                    print(arg, end=" ")
                print("")
    def __outputDebugS(self,info, *args):
        if self.__doLog:
            if mode == 1:
                print("[", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "]", end="", sep="")
                print("[",info,"]", end=" ", sep="")
                for arg in args:
                    print(arg, end="")
                print("")
            else:
                print("[", info, "]", end=" ", sep="")
                for arg in args:
                    print(arg, end="")
                print("")

    def addCommand(self, name, cmd):
        self.__commands[name] = cmd

    def __commandManager(self,msg):
        if mode ==1:
            msgDict = json.loads(msg.payload)
            self.__outputDebugS(INFO, "Received message:\n", json.dumps(msgDict, sort_keys=True, indent=4))
        else:
            msgDict = json.loads(msg)
            self.__outputDebugS(INFO, "Received message:", json.dumps(msgDict))
        outputMsg = {}
        outputMsg["cid"] = msgDict["cid"]
        response = self.__commands.get(msgDict["req"], self.__default)(msgDict["arg"])
        if len(response) > 0:
            outputMsg["res"] = response
        self.__publishMessage("dev/cmd/res", outputMsg)

    def __default(self, req=""):
        self.outputDebug(INFO, "Command not found!")
        return {"info" : "Command not found"}

    def __sendConfig(self):
        outMsg={ "cfg" : {} }
        for param in self.__parameters:
            outMsg["cfg"][param]={ "t" : self.__parameters[param].type, "v" : self.__parameters[param].value }
        self.__publishMessage("dev/cfg",outMsg)

    def __parameterManager(self, msg):
        if mode == 1:
            self.outputDebug(INFO,"Received message: ")
            self.__outputDebugS(INFO,json.loads(msg.payload))
            params = json.loads(msg.payload)
        else:
            self.outputDebug(INFO, "Received message: ")
            self.__outputDebugS(INFO, json.loads(msg))
            params = json.loads(msg)
        for param in params["cfg"]:
            if params["cfg"][param]["t"] == "i32":
                self.__parameters[param].type = INT
            elif params["cfg"][param]["t"] == "str":
                self.__parameters[param].type = STRING
            elif params["cfg"][param]["t"] == "bin":
                self.__parameters[param].type = BINARY
            elif params["cfg"][param]["t"] == "u32":
                self.__parameters[param].type = UINT
            elif params["cfg"][param]["t"] == "f64":
                self.__parameters[param].type = FLOAT

            self.__parameters[param].value = params["cfg"][param]["v"]
        self.__publishMessage("dev/cfg",params)

    def addParameter(self, name, val, type_):
        if type_ == INT:
            val = int(val)
        elif type_ == STRING:
            val = str(val)
        elif type_ == BINARY:
            val = bool(val)
        elif type_ == UINT:
            val = int(val)
        elif type_ == FLOAT:
            val = float(val)
        self.__parameters[name] = LiveObjectsParameter(val, type_)

    def getParameter(self,name):
        if self.__parameters[name].type == INT:
            return int(self.__parameters[name].value)
        elif self.__parameters[name].type == STRING:
            return str(self.__parameters[name].value)
        elif self.__parameters[name].type == BINARY:
            return bool(self.__parameters[name].value)
        elif self.__parameters[name].type == UINT:
            return int(self.__parameters[name].value)
        elif self.__parameters[name].type == FLOAT:
            return float(self.__parameters[name].value)
        return 0

    def addToPayload(self, name, val):
        self.__payload[self.__value][name] = val

    def sendData(self):
        self.__publishMessage("dev/data",self.__payload)
        self.__payload = {}
        self.__payload[self.__value]={}

    def __publishMessage(self, topic, msg):
        self.outputDebug(INFO, "Publishing message on topic: ", topic)
        if mode == 1:
            self.__outputDebugS(INFO, "\n", json.dumps(msg, sort_keys=True, indent=4))
        else:
            self.__outputDebugS(INFO, json.dumps(msg))
        self.__mqtt.publish(topic, json.dumps(msg))

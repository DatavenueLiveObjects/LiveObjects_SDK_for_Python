import paho.mqtt.client as paho
import json
import datetime
import time
from enum import Enum

class Type(Enum):
    INT="i32"
    UINT="u32"
    BINARY="bin"
    STRING="str"
    FLOAT="f64"

class Debug(Enum):
    INFO="INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LiveObjectsParameter:
    def __init__(self,value,type):
        self.value = value
        self.type = type

class LiveObjects:
    def __init__(self, deviceID, port, apiKey, debug = True):
        self.__mqtt = paho.Client(deviceID)
        self.__port = port
        self.__apiKey = apiKey
        self.__parameters = {}
        self.__server = "liveobjects.orange-business.com"
        self.__topic = "dev/data"
        self.__value = "value"
        self.__payload = {self.__value: {}}
        self.__commands = {}
        self.__doLog = debug


    def __onMessage(self,client, userdata, msg):
        if msg.topic == "dev/cfg/upd":
            self.__parameterManager(msg)
        elif msg.topic == "dev/cmd":
            self.__commandManager(msg)

    def __onConnect(self,client, userdata, flags, rc):
        self.outputDebug(Debug.INFO,"Connected with result code "+str(rc))
        if len(self.__commands)>0:
            self.__mqtt.subscribe("dev/cmd")
        if len(self.__parameters)>0:
            self.__mqtt.subscribe("dev/cfg/upd")
            self.__sendConfig()


    def connect(self):
        self.__mqtt.username_pw_set("json+device", self.__apiKey)
        self.__mqtt.on_connect = self.__onConnect
        self.__mqtt.on_message = self.__onMessage
        if self.__port == 8883:
            self.__mqtt.tls_set("certfile.cer")
        self.__mqtt.connect(self.__server, self.__port, 60)
        self.__mqtt.loop_start()
        time.sleep(1)


    def outputDebug(self,info, *args):
        if self.__doLog:
            print("[", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "]", end="", sep="")
            print("[",info,"]", end=" ", sep="")
            for arg in args:
                print(arg, end=" ")
            print("")
    def __outputDebugS(self,info, *args):
        if self.__doLog:
            print("[", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "]", end="", sep="")
            print("[",info,"]", end=" ", sep="")
            for arg in args:
                print(arg, end="")
            print("")

    def addCommand(self, name, cmd):
        self.__commands[name] = cmd

    def __commandManager(self,msg):
        msgDict = json.loads(msg.payload)
        self.__outputDebugS(Debug.INFO, "Received message:\n", json.dumps(msgDict, sort_keys=True, indent=4))
        outputMsg = {}
        outputMsg["cid"] = msgDict["cid"]
        response = self.__commands.get(msgDict["req"], self.__default)(msgDict["arg"])
        if len(response) > 0:
            outputMsg["res"] = response
        self.__publishMessage("dev/cmd/res", outputMsg)

    def __default(self, req=""):
        self.outputDebug(Debug.INFO, "Command not found!")
        return {"info" : "Command not found"}

    def __sendConfig(self):
        outMsg={ "cfg" : {} }
        for param in self.__parameters:
            outMsg["cfg"][param]={ "t" : self.__parameters[param].type.value, "v" : self.__parameters[param].value }
        self.__publishMessage("dev/cfg",outMsg)

    def __parameterManager(self, msg):
        self.outputDebug(Debug.INFO,"Received message: ")
        self.__outputDebugS(Debug.INFO,json.loads(msg.payload))
        params = json.loads(msg.payload)
        for param in params["cfg"]:
            if params["cfg"][param]["t"] == "i32":
                self.__parameters[param].type = Type.INT
            elif params["cfg"][param]["t"] == "str":
                self.__parameters[param].type = Type.STRING
            elif params["cfg"][param]["t"] == "bin":
                self.__parameters[param].type = Type.BINARY
            elif params["cfg"][param]["t"] == "u32":
                self.__parameters[param].type = Type.UINT
            elif params["cfg"][param]["t"] == "f64":
                self.__parameters[param].type = Type.FLOAT

            self.__parameters[param].value = params["cfg"][param]["v"]
        self.__publishMessage("dev/cfg",params)

    def addParameter(self, name, val, type_):
        if type_ == Type.INT:
            val = int(val)
        elif type_ == Type.STRING:
            val = str(val)
        elif type_ == Type.BINARY:
            val = bool(val)
        elif type_ == Type.UINT:
            val = int(val)
        elif type_ == Type.FLOAT:
            val = float(val)
        self.__parameters[name] = LiveObjectsParameter(val, type_)

    def getParameter(self,name):
        if self.__parameters[name].type == Type.INT:
            return int(self.__parameters[name].value)
        elif self.__parameters[name].type == Type.STRING:
            return str(self.__parameters[name].value)
        elif self.__parameters[name].type == Type.BINARY:
            return bool(self.__parameters[name].value)
        elif self.__parameters[name].type == Type.UINT:
            return int(self.__parameters[name].value)
        elif self.__parameters[name].type == Type.FLOAT:
            return float(self.__parameters[name].value)
        return 0

    def addToPayload(self, name, val):
        self.__payload[self.__value][name] = val

    def sendData(self):
        self.__publishMessage("dev/data",self.__payload)
        self.__payload = {}
        self.__payload[self.__value]={}

    def __publishMessage(self, topic, msg):
        self.outputDebug(Debug.INFO, "Publishing message on topic: ", topic)
        self.__outputDebugS(Debug.INFO, "\n", json.dumps(msg, sort_keys=True, indent=4))
        self.__mqtt.publish(topic, json.dumps(msg))
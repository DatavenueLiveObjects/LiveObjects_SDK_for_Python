#
# Copyright (C) Orange
#
# This software is distributed under the terms and conditions of the 'MIT'
# license which can be found in the file 'LICENSE.md' in this package distribution

import sys
import json
import time
import LiveObjects

INT = "i32"
UINT = "u32"
BINARY = "bin"
STRING = "str"
FLOAT = "f64"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

SSL = 8883
NONE = 1883


class LiveObjectsParameter:
    def __init__(self, value, type_, cb=None):
        self.value = value
        self.type = type_
        self.callback = cb


class Connection:
    def __init__(self, debug=True):
        self.__board = LiveObjects.BoardsFactory(net_type=LiveObjects.BoardsInterface.DEFAULT_CARRIER)
        self.mode = self.__board.get_lang_id()

        try:
            if self.mode == LiveObjects.BoardsInterface.PYTHON:
                import paho.mqtt.client as paho
                import os
            elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
                from umqttrobust import MQTTClient
        except ImportError:
            print("[ERROR] U have missing libraries 'Paho-mqtt' (for Python) or 'umqttrobust' (for uPython)")
            sys.exit()

        self.__port = self.__board.get_security_level()
        self.__apiKey = self.__board.get_apikey()
        self.__device_id = self.__board.get_client_id()
        self.__parameters = {}
        self.__server = "mqtt.liveobjects.orange-business.com"
        self.__topic = "dev/data"
        self.__value = "value"
        self.__payload = {self.__value: {}}
        self.__commands = {}
        self.__doLog = debug
        self.quit = False

        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            self.__mqtt = paho.Client(self.__device_id)
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            self.ssl = self.__port == SSL
            self.__mqtt = MQTTClient(self.__device_id, self.__server, self.__port, "json+device",
                                     self.__apiKey, 0, self.ssl, {'server_hostname': self.__server})

    def loop(self):
        if self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            self.__mqtt.check_msg()

    def __on_message(self, client="", userdata="", msg=""):
        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            if msg.topic == "dev/cfg/upd":
                self.__parameter_manager(msg)
            elif msg.topic == "dev/cmd":
                self.__command_manager(msg)
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            if client == b"dev/cfg/upd":
                self.__parameter_manager(userdata)
            elif client == b"dev/cmd":
                self.__command_manager(userdata)

    def __on_connect(self, client="", userdata="", flags="", rc=""):
        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            if rc == 0:
                self.output_debug(INFO, "Connected!")
                if len(self.__commands) > 0:
                    self.output_debug(INFO, "Subscribing commands")
                    self.__mqtt.subscribe("dev/cmd")
                if len(self.__parameters) > 0:
                    self.output_debug(INFO, "Subscribing parameters")
                    self.__mqtt.subscribe("dev/cfg/upd")
                    self.__send_config()
            else:
                self.output_debug(ERROR, "Check your api key")
                self.quit = True
                sys.exit()
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            self.output_debug(INFO, "Connected, sending config")
            if len(self.__commands) > 0:
                self.output_debug(INFO, "Subscribing commands")
                self.__mqtt.subscribe(b"dev/cmd")
            if len(self.__parameters) > 0:
                self.output_debug(INFO, "Subscribing parameters")
                self.__mqtt.subscribe(b"dev/cfg/upd")
                self.__send_config()

    def connect(self):
        self.__board.connect()
        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            self.__mqtt.username_pw_set("json+device", self.__apiKey)
            self.__mqtt.on_connect = self.__on_connect
            self.__mqtt.on_message = self.__on_message
            if self.__port == SSL:
                self.__mqtt.tls_set(self.__board.get_store_cert_filename())
            self.__mqtt.connect(self.__server, self.__port, 60)
            self.__mqtt.loop_start()
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            self.__mqtt.set_callback(self.__on_message)
            self.__mqtt.connect()
            time.sleep(1)
            self.__on_connect()

    def disconnect(self):
        self.__mqtt.disconnect()
        self.output_debug(INFO, "Disconnected")

    def output_debug(self, info, *args):
        if self.__doLog:
            print("[", info, "]", end=" ", sep="")
            for arg in args:
                print(arg, end=" ")
            print("")

    def add_command(self, name, cmd):
        self.__commands[name] = cmd

    def __command_manager(self, msg):
        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            msg_dict = json.loads(msg.payload)
            self.output_debug(INFO, "Received message:\n", json.dumps(msg_dict, sort_keys=True, indent=4))
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            msg_dict = json.loads(msg)
            self.output_debug(INFO, "Received message:", json.dumps(msg_dict))
        output_msg = {}
        output_msg["cid"] = msg_dict["cid"]
        response = self.__commands.get(msg_dict["req"], self.__default)(msg_dict["arg"])
        if len(response) > 0:
            output_msg["res"] = response
        self.__publish_message("dev/cmd/res", output_msg)

    def __default(self, req=""):
        self.output_debug(INFO, "Command not found!")
        return {"info": "Command not found"}

    def __send_config(self):
        out_msg = {"cfg": {}}
        for param in self.__parameters:
            out_msg["cfg"][param] = {"t": self.__parameters[param].type, "v": self.__parameters[param].value}
        self.__publish_message("dev/cfg", out_msg)

    def __parameter_manager(self, msg):
        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            self.output_debug(INFO, "Received message: ")
            self.output_debug(INFO, json.loads(msg.payload))
            params = json.loads(msg.payload)
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            self.output_debug(INFO, "Received message: ")
            self.output_debug(INFO, json.loads(msg))
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
            if self.__parameters[param].callback is not None:
                self.__parameters[param].callback(param, params["cfg"][param]["v"])
        self.__publish_message("dev/cfg", params)

    def add_parameter(self, name, val, type_, cb=None):
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
        self.__parameters[name] = LiveObjectsParameter(val, type_, cb)

    def get_parameter(self, name):
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

    def add_to_payload(self, name, val):
        self.__payload[self.__value][name] = val
    
    def set_object_as_payload(self, val):
        self.__payload[self.__value] = val

    def add_model(self, model):
        self.__payload["model"] = model

    def add_tag(self, tag):
        if "tags" not in self.__payload:
            self.__payload["tags"] = []
        self.__payload["tags"].append(tag)

    def add_tags(self, tags):
        if "tags" not in self.__payload:
            self.__payload["tags"] = []
        for tag in tags:
            self.__payload["tags"].append(tag)

    def send_data(self):
        if self.quit:
            sys.exit()
        self.__publish_message("dev/data", self.__payload)
        self.__payload = {}
        self.__payload[self.__value] = {}

    def __publish_message(self, topic, msg):
        self.output_debug(INFO, "Publishing message on topic: ", topic)

        if self.mode == LiveObjects.BoardsInterface.PYTHON:
            self.output_debug(INFO, "\n", json.dumps(msg, sort_keys=True, indent=4))
        elif self.mode == LiveObjects.BoardsInterface.MICROPYTHON:
            self.output_debug(INFO, json.dumps(msg))

        self.__mqtt.publish(topic, json.dumps(msg))

# Prototype with Orange using Live Objects
### Discover Orange  [**Live Objects**](https://liveobjects.orange-business.com) using dedicated SDK for **Python and uPython compatible** boards and systems.

This code wraps all the functions necessary to make your object work with Live Objects.

 You can declare parameters, which you can later update OTA from Live objects. You can also create commands to trigger actions remotely.
 Only thing u must do yourself is connecting the board with internet.

Code uses MQTT connection to exchange data with Live objects under the hood to keep your parameters up to date or execute the commands received without you having to take care of them (apart from writing the code of these commands, of course).

## Compatibility ##
| System | MQTT | MQTTS |
| :--- | :---: | :---: |
| Linux | OK |OK |
| Windows | OK |OK |
| Raspberry Pi | OK |OK |
| ESP8266 | OK | - |
| ESP32 | OK | OK |

## Prerequisites/dependecies ##
This code needs a few libraries to run
- Python needs [paho-mqtt](https://pypi.org/project/paho-mqtt/)
- uPython needs [umqttsimple, umqttrobust and ssl](https://github.com/micropython/micropython-lib)

## How to use ##

1. Log in to [Live Objects](https://liveobjects.orange-business.com) or request a [trial account](https://liveobjects.orange-business.com/#/request_account) (up to 10 devices for 1 year) if you don't have one.
2. Create an [API key](https://liveobjects.orange-business.com/#/administration/apikeys) for your device. Give it a name, select the *Device access* role and validate. Copy the key.
3. Clone or download the directory from Github.
4. Change **\<APIKEY\>** in sketches to one you generated
5. Run script

## Developer guide ##

### Declare parameters ###
You can update over the air some parameters of your sketch using Live Objects's parameters. Parameters and Commands must be declared **before** your device connects to Live Objects.

You can declare parameters with the `addParameter()` instruction, which accepts the following arguments:
- the label of your parameter as it will be displayed on Live Objects;
- the value of parameter
- parameter type [INT STRING FLOAT BINARY]
- (optional) a callback function, if you need to perform some tasks after the parameter has been updated

To retrieve a parameter use function `getParameter()` which takes following arguments:
- Parameter name

Example:
```Python
lo.addParameter("messageRate", 25, INT);
lo.addParameter("sendDHTData", true ,BINARY, myCallbackFunction);
...
if lo.getParameter("sendDHTData"):
    lo.addToPayload("temperature",DHT.readTemeprature())
    lo.addToPayload("humidity",DHT.readHumidity())
```

The callback function takes 2 arguments
```Python
def myCallbackFunction(parameterName, newValue):
  // do stuff
```

Further reading on Live Objects' [Parameters](https://liveobjects.orange-business.com/doc/html/lo_manual.html#_configuration).

### Declare commands ###
Commands lets you trigger specific actions on your device from Live Objects. Parameters and Commands must be declared _before_ your device connects to Live Objects.

Commands can be declared using the `addcommand()` instruction, which accepts the following arguments:
- the label of your command
- the callback function that will execute the command.
```Python
lo.addParameter("a command", myCallback);
```

The callback function should take 1 parameter and return dictonary
```Python
def myCallback(args={}):
  // do stuff
  return {}
```

Arguments and response are optional when using commands, but they can be useful if you want to pass parameters to your function. For instance, you could define a `play tone` command that will use some parameters like the frequency of the tone, or its duration.
- Any incoming arguments will be passed as member of a dictonary
- You can pass response arguments in the form of a dictonary by returning them
```Python
def playTone(args={}):
  duration = args["duration"]
  frequency = args["frequency"]
  // play the tone accordingly to arguments
  ...
  return {"I played":"the tone"}
}

def setup():
  lo.addCommand("play tone", playTone)
```
> :warning: **Command name and arguments are case-sensitive when creating the command on Live Objects.**: On the opposite, there is no specific order for specifying the command arguments.

Further reading on Live Objects' [Commands](https://liveobjects.orange-business.com/doc/html/lo_manual.html#MQTT_DEV_CMD).

### Sending data ###
You can send data very easily to Live Objects.

#### Dead simple method ####
Compose your payload using the `addToPayload()` instruction. You will need to provide a label for your value, and the data itself. You data can be of any simple type.

Data is added on each call to `addToPayload()`, so repeat the instruction if you have multiple data to send. When your payload is ready, send it using `sendData()`. That simple.
```Python
value=21
myOtherValue=37

def foo():
  // collect data
  lo.addToPayload("my data", value)
  lo.addToPayload("my other data", myOtherValue)
  lo.sendData() # send to LiveObjects
```

As soon the data is send, your payload is cleared and waiting for the next sending.


### Connect, disconnect and loop ###
You can control the connection and disconnection of your device using `connect()` and `disconnect()`.



In order to check for any incoming configuration update or command, you need to keep the `loop()` instruction in your main loop.
```Python
def foo():
  lo.connect();
  while True:
     #Do some stuff
     #...
     lo.loop(); #Keep this in main loop
}
```

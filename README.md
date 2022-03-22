# Prototype with Orange using Live Objects
### Discover Orange  [**Live Objects**](https://liveobjects.orange-business.com) using dedicated SDK for **Python and uPython compatible** boards and systems.

This code wraps all the functions necessary to make your object work with Live Objects.

 You can declare parameters, which you can later update OTA from Live objects. You can also create commands to trigger actions remotely.
 Only thing you must do yourself is connecting the board with internet.

Code uses MQTT connection to exchange data with Live objects under the hood to keep your parameters up to date or execute the commands received without you having to take care of them (apart from writing the code of these commands, of course).

## Compatibility ##
| System        | Connectivity    | MQTT | MQTTS |
|:--------------|-----------------|:----:|:-----:|
| Linux         | Delivered by OS |  OK  |  OK   |
| Windows       | Delivered by OS |  OK  |  OK   |
| Raspberry Pi  | Delivered by OS |  OK  |  OK   |
| ESP8266       | WiFi            |  OK  |   -   |
| ESP32         | WiFi            |  OK  |  OK   |
| LoPy (Pycom)  | WiFi            |  OK  |   -   |
| GPy (Pycom)   | WiFi, LTE       |  OK  |   -   |

## Prerequisites / dependecies ##
This code needs a few libraries to run:
- Python needs [paho-mqtt](https://pypi.org/project/paho-mqtt/)
    - Python for Windows needs [python-certifi-win32](https://pypi.org/project/python-certifi-win32/)
- uPython needs [umqttsimple, umqttrobust and ssl](https://github.com/micropython/micropython-lib)

## How to use ##

1. Log in to [Live Objects](https://liveobjects.orange-business.com) or request a [trial account](https://liveobjects.orange-business.com/#/request_account) (up to 10 devices for 1 year) if you don't have one,
2. Create an [API key](https://liveobjects.orange-business.com/#/administration/apikeys) for your device. Give it a name, select the *Device access* role and validate. Copy the key,
3. Clone or download the directory from Github,
4. Change **\<APIKEY\>** in `credentials.py` to one you generated,
5. Run selected `.py` script

## Developer guide ##

### Constructor ###

Constructor of LiveObjects looks like below:

```Python
lo = LiveObjects.Connection()
```

### Debug messages ###

You can use LiveObjects to output debug messages.
```Python
VALUE = 21
# INFO / ERROR / WARNING
lo.outputDebug(LiveObjects.INFO, "example value", VALUE, ...)
# Output: [INFO] example value 21 ...
```

### Declare parameters ###
You can update over the air some parameters of your script using Live Objects's parameters. Parameters and Commands must be declared **before** your device connects to Live Objects.

You can declare parameters with the `addParameter()` instruction, which accepts the following arguments:
- the label of your parameter as it will be displayed on Live Objects;
- the value of parameter
- parameter type [INT STRING FLOAT BINARY]
- (optional) a callback function, if you need to perform some tasks after the parameter has been updated

To retrieve a parameter use function `getParameter()` which takes following arguments:
- Parameter name

Example:
```Python
lo.addParameter("messageRate", 25, LiveObjects.INT)
lo.addParameter("sendDHTData", true, LiveObjects.BINARY, myCallbackFunction)
# ...
if lo.getParameter("sendDHTData"):
    lo.addToPayload("temperature", DHT.readTemeprature())
    lo.addToPayload("humidity", DHT.readHumidity())
```

The callback function takes 2 arguments:
```Python
def myCallbackFunction(parameterName, newValue):
    # do stuff
```

Further reading on Live Objects' [Parameters](https://liveobjects.orange-business.com/doc/html/lo_manual.html#_configuration).

### Declare commands ###
Commands let you trigger specific actions on your device from Live Objects. Parameters and Commands must be declared _before_ your device connects to Live Objects.

Commands can be declared using the `addcommand()` instruction, which accepts the following arguments:
- the label of your command
- the callback function that will execute the command.
```Python
lo.addParameter("a command", myCallback);
```

The callback function should take 1 parameter and return dictionary:
```Python
def myCallback(args={}):
    # do stuff
    return {}
```

Arguments and response are optional when using commands, but they can be useful if you want to pass parameters to your function. For instance, you could define a `play tone` command that will use some parameters like the frequency of the tone, or its duration.
- Any incoming arguments will be passed as member of a dictionary
- You can pass response arguments in the form of a dictionary by returning them
```Python
def playTone(args={}):
    duration = args["duration"]
    frequency = args["frequency"]
    # play the tone accordingly to arguments
    # ...
    return {"I played": "the tone"}

def setup():
    lo.addCommand("play tone", playTone)
```
> Warning: **Command name and arguments are case-sensitive when creating the command on Live Objects.**: On the opposite, there is no specific order for specifying the command arguments.

Further reading on Live Objects' [Commands](https://liveobjects.orange-business.com/doc/html/lo_manual.html#MQTT_DEV_CMD).

### Sending data ###
You can send data very easily to Live Objects.

#### Dead simple method ####
Compose your payload using the `addToPayload()` instruction. You will need to provide a label for your value, and the data itself. Your data can be of any simple type.

Data is added on each call to `addToPayload()`, so repeat the instruction if you have multiple data to send. When your payload is ready, send it using `sendData()`. That simple.
```Python
VALUE = 21
MY_OTHER_VALUE = 37

def foo():
    # collect data
    lo.addToPayload("my data", VALUE)
    lo.addToPayload("my other data", MY_OTHER_VALUE)
    lo.sendData() # send to LiveObjects
```

As soon the data is sent, your payload is cleared and waiting for the next sending.

### Advanced payload features ###
```Python
# Add "model" property to your message
lo.addModel("exampleName")

# Add "tag" property to your message
lo.addTag("kitchen")
lo.addTags(["humidity", "bathroom"])

# Use your object as payload (this function doesn't append current payload)
obj = {"example":"value", "example2":"value2"}
lo.setObjectAsPayload(obj)
```


### Connect, disconnect and loop ###
You can control the connection and disconnection of your device using `connect()` and `disconnect()`.


In order to check for any incoming configuration update or command, you need to keep the `loop()` instruction in your main loop.
```Python
def foo():
    lo.connect();
    while True:
        # Do some stuff
        #...
        lo.loop(); #Keep this in main loop
    lo.disconnect()
```


# Installation guide for uPython #
## Example for ESP32 / ESP8266 ##
### Requirements ###
1. [ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy)
2. [umqttsimple, umqttrobust and ssl](https://github.com/micropython/micropython-lib)
3. [PuTTY](https://www.putty.org/) (for Windows)

### Installation steps ###

1. Preparation 

Change **\<APIKEY\>** in `credentials.py` to one you generated.\
Change **\<WIFI_SSID\>** and **\<WIFI_PASS\>** suitable to your WiFi.


2. Copy files into device
```Shell
>ampy -pCOMXX put umqttrobust.py 
>ampy -pCOMXX put simple.py   
>ampy -pCOMXX put LiveObjects // It will copy directory with its content 
```
3. Prepare your script and save it as `main.py` then copy file into device. You can use one of example ones (`1_send_data.py`, ...) renaming it to `main.py` 
```Shell
>ampy -pCOMXX put main.py
```

4. Connect to device and check if it's working using PuTTY
    
    Ctrl + D soft resets device

    Ctrl + C Stops currently running script

### Summary ###
After all steps content of the device should look like below:
```Shell
>ampy -pCOMXX ls
/LiveObjects
/boot.py
/main.py
/umqttrobust.py
/simple.py

>ampy -pCOMXX ls LiveObjects
/LiveObjects/Connection.py
/LiveObjects/__init__.py
/LiveObjects/hal.py
/LiveObjects/credentials.py
```

## Example for LoPy / GPy ##

You can do the steps as above but better is to use [Pymakr plug-in](https://pycom.io/products/supported-networks/pymakr/) for **Visual Studio Code** or **Atom** delivered by [Pycom](https://pycom.io/). Plug-in supports code development, its upload to board and communication with board. 

## Troubleshooting ##
If you are getting 'MQTT exception: 5' check your api key
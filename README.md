# Prototype with Orange using Live Objects
### Discover Orange  [**Live Objects**](https://liveobjects.orange-business.com) using dedicated SDK for **Python and uPython compatible** boards and systems.

This code wraps all the functions necessary to make your object work with Live Objects.

You can declare parameters, which you can later update OTA from Live objects. You can also create commands to trigger actions remotely.
Only thing you must do yourself is connecting the board with internet.

Code uses MQTT connection to exchange data with Live objects under the hood to keep your parameters up to date or execute the commands received without you having to take care of them (apart from writing the code of these commands, of course).

## Compatibility ##
| System        | MQTT | MQTTS |
|:--------------|:----:|:-----:|
| Linux         |  OK  |  OK   |
| Windows       |  OK  |  OK   |
| Raspberry Pi  |  OK  |  OK   |
| ESP8266       |  OK  |   -   |
| ESP32         |  OK  |  OK   |
| LoPy (Pycom)  |  OK  |   -   |
| GPy (Pycom)   |  OK  |   -   |

## Prerequisites / dependencies ##
This code needs a few libraries to run:
- Python needs [paho-mqtt](https://pypi.org/project/paho-mqtt/)
    - Python for Windows needs [python-certifi-win32](https://pypi.org/project/python-certifi-win32/)
- uPython needs [umqttsimple, umqttrobust and ssl](https://github.com/micropython/micropython-lib)

## How to use ##

1. Log in to [Live Objects](https://liveobjects.orange-business.com) or request a [trial account](https://liveobjects.orange-business.com/#/request_account) (up to 10 devices for 1 year) if you don't have one,
2. Create an [API key](https://liveobjects.orange-business.com/#/administration/apikeys) for your device. Give it a name, select the *Device access* role and validate. Copy the key,
3. Clone or download the directory from GitHub,
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
lo.output_debug(LiveObjects.INFO, "example value", VALUE, ...)
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
lo.add_parameter("message_rate", 25, LiveObjects.INT)
lo.add_parameter("send_DHT_data", true, LiveObjects.BINARY, my_callback_function)
# ...
if lo.get_parameter("send_DHT_data"):
    lo.add_to_payload("temperature", DHT.read_temeprature())
    lo.add_to_payload("humidity", DHT.read_humidity())
```

The callback function takes 2 arguments:
```Python
def my_callback_function(parameter_name, new_value):
    # do stuff
```

Further reading on Live Objects' [Parameters](https://liveobjects.orange-business.com/doc/html/lo_manual.html#_configuration).

### Declare commands ###
Commands let you trigger specific actions on your device from Live Objects. Parameters and Commands must be declared _before_ your device connects to Live Objects.

Commands can be declared using the `addcommand()` instruction, which accepts the following arguments:
- the label of your command
- the callback function that will execute the command.

```Python
lo.add_parameter("a command", my_callback, );
```

The callback function should take 1 parameter and return dictionary:
```Python
def my_callback(args={}):
    # do stuff
    return {}
```

Arguments and response are optional when using commands, but they can be useful if you want to pass parameters to your function. For instance, you could define a `play tone` command that will use some parameters like the frequency of the tone, or its duration.
- Any incoming arguments will be passed as member of a dictionary
- You can pass response arguments in the form of a dictionary by returning them

```Python
def play_tone(args={}):
    duration = args["duration"]
    frequency = args["frequency"]
    # play the tone accordingly to arguments
    # ...
    return {"I played": "the tone"}


def setup():
    lo.add_command("play tone", play_tone)
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
    lo.add_to_payload("my data", VALUE)
    lo.add_to_payload("my other data", MY_OTHER_VALUE)
    lo.send_data()  # send to LiveObjects
```

As soon the data is sent, your payload is cleared and waiting for the next sending.

### Advanced payload features ###

```Python
# Add "model" property to your message
lo.add_model("example_name")

# Add "tag" property to your message
lo.add_tag("kitchen")
lo.add_tags(["humidity", "bathroom"])

# Use your object as payload (this function doesn't append current payload)
obj = {"example": "value", "example2": "value2"}
lo.set_object_as_payload(obj)
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

### Changing default carrier to connect to the network ###

Every board has its own default carrier for connection to the network (see below). 

| System        | Default carrier | Optional carrier |
|:--------------|:---------------:|:----------------:|
| Linux         | Delivered by OS |        -         |
| Windows       | Delivered by OS |        -         |
| Raspberry Pi  | Delivered by OS |        -         |
| ESP8266       |      Wi-Fi      |        -         |
| ESP32         |      Wi-Fi      |        -         |
| LoPy (Pycom)  |      Wi-Fi      |        -         |
| GPy (Pycom)   |      Wi-Fi      |       LTE        |

For GPy you can switch connectivity to optional carrier. You need to do change in `Connection` class in `Connection.py`
from:
```Python
def __init__(self, debug=True):
    self.__board = LiveObjects.BoardsFactory(net_type=LiveObjects.BoardsInterface.DEFAULT_CARRIER)
...
```
to:
```Python
def __init__(self, debug=True):
    self.__board = LiveObjects.BoardsFactory(net_type=LiveObjects.BoardsInterface.LTE)
...
```
Then GPy will connect via LTE network.

### Adding new boards ###

There is possibility to add your new type of board supporting Python/uPython. 
You need to add your own class in `hal.py`. Name of this class has to be the same as output of `sys.platform`
and has to start from capital letter.
```commandline
>>> sys.platform
'GPy'
>>> 
```
Below code shows basic constructor:
```Python
def __init__(self, net_type):
    self._lang_id = BoardsInterface.MICROPYTHON
    self._net_type = BoardsInterface.WIFI if net_type == BoardsInterface.DEFAULT_CARRIER else net_type
    self._carrier_capability = (BoardsInterface.WIFI,)
    self._wifi_tls_capability = False
    self._credentials = super().create_credentials(self._net_type)
```
Basic fields meaning:
- **_lang_id**: used Python dialect: PYTHON / MICROPYTHON,
- **_net_type**: used type of network: WIFI / LTE / network delivered by OS / ...
- **_carrier_capability**: _tuple_ containing supported type(s) of network,
- **_wifi_tls_capability**: _True_ if TLS is supported and MQTTS could be used, 
- **_credentials**: required credentials depended on network type: SSID/PASS for Wi-Fi, PIN/APN for LTE etc. 

If other specific fields are necessary you need to define them.
You need to override specific methods - e.g. `connect` which is depended on type of board. 
All specific functions are placed in `services.py`. 
If your board needs function supporting its equipment you need to put it in this file.   


# Installation guide for uPython #
## Example for ESP32 / ESP8266 ##
### Requirements ###
1. [ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy)
2. [umqttsimple, umqttrobust and ssl](https://github.com/micropython/micropython-lib)
3. [PuTTY](https://www.putty.org/) (for Windows)

### Installation steps ###

1. Preparation 

Change **\<APIKEY\>** in `credentials.py` to one you generated.\
Change **\<WIFI_SSID\>** and **\<WIFI_PASS\>** suitable to your Wi-Fi or 
change **\<PIN\>** and **\<APN\>** suitable to your SIM card.

2. Copy files into device
```commandline
> ampy -pCOMXX put umqttrobust.py 
> ampy -pCOMXX put simple.py   
> ampy -pCOMXX put LiveObjects // It will copy directory with its content 
```
3. Prepare your script and save it as `main.py` then copy file into device. 
You can use one of example ones (`1_send_data.py`, ...) renaming it to `main.py` 
```Shell
> ampy -pCOMXX put main.py
```

4. Connect to device and check if it's working using PuTTY
    
    Ctrl + D soft resets device

    Ctrl + C Stops currently running script

### Summary ###

After all steps content of the device should look like below:
```commandline
> ampy -pCOMXX ls
/LiveObjects
/boot.py
/main.py
/umqttrobust.py
/simple.py

> ampy -pCOMXX ls LiveObjects
/LiveObjects/Connection.py
/LiveObjects/__init__.py
/LiveObjects/hal.py
/LiveObjects/credentials.py
/LiveObjects/services.py
```

## Example for LoPy / GPy ##

You can do the steps as above but better is to use [Pymakr plug-in](https://pycom.io/products/supported-networks/pymakr/) for **Visual Studio Code** or **Atom** delivered by [Pycom](https://pycom.io/). 
Plug-in supports code development, its upload to the board and communication with board. 

## Troubleshooting ##
If you are getting 'MQTT exception: 5' check your api key
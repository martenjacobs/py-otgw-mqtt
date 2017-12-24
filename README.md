# Python OTGW MQTT bridge

This package allows for communication between an OpenTherm Gateway, running the [firmware by Schelte Bron](http://otgw.tclcode.com/) and an MQTT service. It was tested using [Home Assistant](http://www.home-assistant.io)'s built-in MQTT broker.

## Supported OTGW gateway communication protocols
Currently, only direct serial communication is supported, but implementing further types is pretty easy. I'm open to pull requests.

## Supported MQTT brokers
The MQTT client used is [paho](https://www.eclipse.org/paho/). It's one of the most widely-used MQTT clients for Python, so it should work on most brokers. If you're having problems with a certain type, please open an issue or send me a pull request with a fix.

## Configuration
The configuration for the bridge is located in config.json.

### Example configuration
```json
{
    "otgw" : {
        "type": "serial",
        "device": "/dev/ttyUSB0",
        "baudrate": 9600
    },
    "mqtt" : {
        "client_id": "otgw",
        "host": "127.0.0.1",
        "port": 1883,
        "keepalive": 60,
        "bind_address": "",
        "username": null,
        "password": null,
        "qos": 0,
        "pub_topic_namespace": "value/otgw",
        "sub_topic_namespace": "set/otgw"
    }
}
```

## Installation
To install this script as a daemon, run the following commands (on a Debian-based distribution):

1. Install dependencies:
   ```bash
   sudo apt install python python-serial
   ```
2. Create a new folder, for example:
   ```bash
   sudo mkdir -p /usr/lib/py-otgw-mqtt
   cd /usr/lib/py-otgw-mqtt
   ```
3. Clone this repository into the current directory:
   ```bash
   sudo git clone https://github.com/martenjacobs/py-otgw-mqtt.git .
   ```
4. Change `config.json` with your favorite text editor
5. Copy the service file to the systemd directory. If you used a different folder name than `/usr/lib/py-otgw-mqtt` you will need to change the `WorkingDirectory` in the file first.
   ```bash
   sudo cp ./py-otgw-mqtt.service /etc/systemd/system/
   ```
6. Enable the service so it starts up on boot:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable py-otgw-mqtt.service
   ```
7. Start up the service
   ```bash
   sudo systemctl start py-otgw-mqtt.service
   ```
8. View the log to see if everything works
   ```bash
   journalctl -u py-otgw-mqtt.service -f
   ```

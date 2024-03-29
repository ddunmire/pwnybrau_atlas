#Write Sensor output to an Topic on an MQTT Broker
This quick example will who you how to run AtlasPH or AtlasTEMP and redirect its output to a MQTT broker.  

This example allows you manually pull measurements from the I2C bus and publish them to a MQTT Broker using either of these two scripts:
1. atlas_ph_pub2mqtt.sh
2. atlas_temp_pub2mqtt.sh

As a bonus, the following systemd files can be enabled to turn those scripts into a service.
1. atlas_ph_pub2mqtt.service
2. atlas_temp_pub2mqtt.service

    systemctl enable "[path]/examples/mqtt/bin/atlas_ph_pub2mqtt"
     systemctl enable "[path]/examples/mqtt/bin/atlas_temp_pub2mqtt"

# MQTT stanza defines information required to communicate sensor measurements to a MQTT broker.
[MQTT]
# MQTT broker service
broker = test.mosquitto.org  

# MQTT broker listening port
#   TCP[no auth]            : 1883
#   TCP[auth]               : 1884
#   TLS[encrypted & no auth]: 8883
port = 1884

# User Credentials presented to the MQTT server.
#   Note: server could be configured to use CN Name instead (see use_CN_as_username).
#         This would override username here.
username = rw
password = readwrite

# Toggle on/off attempt to use TLS encryption.
use_TLS = false

# Use the client certificates CN name - ignoring username.
use_CN_as_username = false

# Toggle on/off client side validation of the server's public certificate.  
#     Probably not a good idea for production
use_insecure_tls = true

# Paths to certificates
caCertPath = /path/to/ca.crt
certfile = /path/to/client.crt
keyfile = /path/to/client.key

# topicPath is a prefix added to the sensor's name.  
# The sensor's name is defined on the CLI using the --name parameter. 
#   suntax:
#     FULL TOPIC = topic = topicPath + name 
#   example:   
#     if:  topicPath = pwnybrau/sensors/
#     and if cli:  atlasPH.py --name = AtlasPH ...
#     
#     topic = pwnybrau/sensors/AtlasPH   <- message published to the broker on this topic name.
topicPath = your_system/sensors/
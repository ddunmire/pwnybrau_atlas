#!/bin/sh
# pwnybrau_read_AtlasTEMP_stdout.sh
# Simple shortcut script to be called by a splunk univeral forwarder
# Scripts calls python3 based script: AtlasTEMP.py
#    OUTPUT: json :  timestamp,Temperature, unit
#    Sample output:  {"timestamp":"2019-11-15T21:45:21.400057+00:00", "name":"AtlasRTD", "measurement":"78.919", "Unit":"f"}
#                    {"timestamp":"2019-11-15T21:45:21.400057+00:00", "name":"AtlasRTD", "measurement":"78.919", "Unit":"f", "sensor":{"type":"pH", "firmware":2.12}}
#
export output="MQTT"              # output destination: STDOUT, MQTT, LOG, or HEC
#export output="STDOUT"
export output_config="../local/publish_mosquitto.conf"   # output configuration file for defining endpoint
export listentime=-1              # total time to take measurements (note -1 = infinity)
export sleeptime=10               # time to wait between measurements
export unit="f"                   # temperature unit: c,f or k
#export i2cbus=1                  # i2c bus number to use:  default = 1
#export i2caddress=102            # i2c address for PH device:  default = 102

# Note --show_device_info         # print atlas device info

###########
## START

# is python3 installed?
command -v python3 > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Could not find python3.  Exiting..."
  exit 1
fi

# execute sevice
python3 ../../../src/AtlasTEMP.py --output=${output} --output_config=${output_config}  --listentime=${listentime} --sleeptime=${sleeptime} --unit=${unit} --show_device_info


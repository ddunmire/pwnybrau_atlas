#!/bin/sh

# atlasPH_pub2edge.sh
# Scripts calls python3 based script: AtlasPH.py and published output to mqtt broker.
#   The MQTT setting are defined in ../local/publish_edge.conf
#
#    OUTPUT: json :  timestamp,Temperature, unit
#    Sample output:   {"timestamp":"2019-11-18T01:49:10.927006+00:00", "name": "AtlasPH", "measurement":"3.768"}
#                     {"timestamp":"2019-11-18T01:49:10.927006+00:00", "name": "AtlasPH", "measurement":"3.768", "sensor":{"type":"pH", "firmware":2.12}}
#
export output="MQTT"                                # output destination: STDOUT, MQTT, LOG or HEC
#export output="STDOUT"
export output_config="../local/publish_mosquitto.conf"   # output configuration file for defining endpoint
export listentime=-1                                 # total time to take measurements (note -1 = infinity)
export sleeptime=10                                  # time to wait between measurements
#export i2cbus=1                                    # i2c bus number to use:  default = 1
#export i2caddress=99                               # i2c address for PH device:  default = 99

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
#echo "python3 ../../../src/AtlasPH.py --output=${output} --output_config=\"${output_config}\" --listentime=${listentime} --sleeptime=${sleeptime} --show_device_info"
python3 ../../../src/AtlasPH.py --debug --output=${output} --output_config=${output_config} --listentime=${listentime} --sleeptime=${sleeptime} --show_device_info
#python3 ../../../src/AtlasPH.py --output=${output} --output_config=${output_config} --listentime=${listentime} --sleeptime=${sleeptime} --show_device_info


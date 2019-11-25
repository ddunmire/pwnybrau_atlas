#!/bin/sh

# pwnybrau_read_AtlasTEMP_stdout.sh
# Simple shortcut script to be called by a splunk univeral forwarder
# Scripts calls python3 based script: AtlasTEMP.py
#    OUTPUT: json :  timestamp,Temperature, unit
#    Sample output:  {"timestamp":"2019-11-15T21:45:21.400057+00:00", "ChamberTemp":"78.919", "Unit":"f"}
#
export output="STDOUT"            # output destination: STDOUT, LOG or HEC
#export logfile="pwnybrau_ph.log" # USED only with output=LOG
export listentime=1               # total time to take measurements (note -1 = infinity)
export sleeptime=1                # time to wait between measurements
export unit="f"                   # temperature unit: c,f or k
#export i2cbus=1                  # i2c bus number to use:  default = 1
#export i2caddress=102            # i2c address for PH device:  default = 102

# Note --show_device_info         # print atlas device info

# execute sevice
if [ -z ${SPLUNK_HOME} ]; then
   DIRECTORY=$(cd `dirname $0` && pwd)
   echo $DIRECTORY
   python3 $DIRECTORY/AtlasTEMP.py --output=${output} --listentime=${listentime} --sleeptime=${sleeptime} --unit=${unit}
else
   python3 $SPLUNK_HOME/etc/apps/pwnybrau_atlas/bin/AtlasTEMP.py --output=${output} --listentime=${listentime} --sleeptime=${sleeptime} --unit=${unit}
fi

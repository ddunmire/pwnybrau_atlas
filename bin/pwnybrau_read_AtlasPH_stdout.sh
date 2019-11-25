#!/bin/sh

# pwnybrau_read_AtlasPH_stdout.sh
# Simple shortcut script to be called by a splunk univeral forwarder
# Scripts calls python3 based script: AtlasPH.py
#    OUTPUT: json :  timestamp,Temperature, unit
#    Sample output:  {"timestamp":"2019-11-18T01:49:10.927006+00:00", "PH":"3.768", "Device":"?I,pH,2.12"}
#
#
export output="STDOUT"            # output destination: STDOUT, LOG or HEC
#export logfile="pwnybrau_ph.log" # USED only with output=LOG
export listentime=1               # total time to take measurements (note -1 = infinity)
export sleeptime=1                # time to wait between measurements
#export i2cbus=1                  # i2c bus number to use:  default = 1
#export i2caddress=99             # i2c address for PH device:  default = 99

# Note --show_device_info         # print atlas device info

# execute sevice
if [ -z ${SPLUNK_HOME} ]; then
   DIRECTORY=$(cd `dirname $0` && pwd)
   echo $DIRECTORY
   python3 $DIRECTORY/AtlasPH.py --output=${output} --listentime=${listentime} --sleeptime=${sleeptime}
else
   python3 $SPLUNK_HOME/etc/apps/pwnybrau_atlas/bin/AtlasPH.py --output=${output} --listentime=${listentime} --sleeptime=${sleeptime}
fi

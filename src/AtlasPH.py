#!/usr/bin/python3

import atexit     	#used for graceful exit of script (close io)
import argparse   	#used to parse cmdline arguements to this script
import configparser #parse configuration files (like local/splunk_server.conf)

import io         	# used to create file streams
#from io import open
import fcntl      	# used to access I2C parameters like addresses

import datetime   	# used to form timestamp
import time       	# used for sleep delay and timestamps
import string     	# helps parse strings

import os
import sys

from pwnybrau_library.publisherfactory import PublisherFactory
from pwnybrau_library.publisher import Publisher
from atlas_i2c import sensors, commands

def main():
	###### Parse Arguements
	parser = argparse.ArgumentParser(description='AtlasPH.py will poll an atlas scientific EZO-pH Temperature circuit via i2c.')
	parser.add_argument("--output", type=str, default="STDOUT", choices=PublisherFactory.PublisherTypes, help="Where to output measurements: (Default: STDOUT)".join(PublisherFactory.PublisherTypes))
	parser.add_argument("--output_config", type=str, default="publish.conf", help="Path and file name of the config file with our output params.  Used with LOG, MQTT and HEC")
	#parser.add_argument("--logfile", default="./AtlasPH", help="Sets file path into which output measurements are appended. Only used with --output=LOG.   (Default: ./AtlasPH.[year].[day].log)")
	#parser.add_argument("--loglevel", default="INFO", help="script logging level for messages (default: INFO) INFO, DEBUG, WARN, WARNING, ERROR")
	parser.add_argument("--listentime", type=float, default=-1, help="How the script will run (in seconds) before exiting.  (default=-1 run forever)")
	parser.add_argument("--sleeptime", type=float, default=1, help="How long to wait between measurement (in seconds) before exiting.  example: --sleeptime=.3 = 300ms (default=1s)")
	parser.add_argument("--i2cbus", type=int, default=1, help="I2C Bus Number to query [integer] (example: /dev/i2c-X)  (default=0)")
	parser.add_argument("--i2caddress", type=int, default=99, help="Device Address [integer] on the bus (example: 99 (hex 0x63) )  (default=99)")
	parser.add_argument("--show_device_info", default=False, action='store_true', help="Optional Flag: Display device info is set.")
	parser.add_argument("--name", type=str, default="AtlasPH", help="Sensor Name.")
	args=parser.parse_args()

	###### Create Atlas I2C object to read the RTD
	deviceInfo = "NONE"
	sensor = ""
	outputter:Publisher = PublisherFactory.factory(args)

	try:
		sensor = sensors.Sensor("pH", address=args.i2caddress)  #TODO: add bus
		sensor.client.bus = args.i2cbus	
		sensor.client.device_file.close()							
		sensor.client.open_file()
		sensor.connect()

		###### Define graceful exit
		atexit.register(sensor.client.close)
	
	except FileNotFoundError as err:
		errMsg = "ERROR:  I2C bus not found.  Verify existance of: " + err.filename
		sys.exit(errMsg)

	##### Device config
	try:
		##get Atlas EZO unit info (if --show_device_info) 
		if (args.show_device_info):
			deviceInfo = sensor.query(commands.INFO)
			deviceInfo = deviceInfo.data.decode("utf-8").split(",")
			sensor_info_template = '{{"type":"{deviceType}", "firmware":{firmware}}}'
			deviceInfo=sensor_info_template.format(deviceType=deviceInfo[1], firmware=deviceInfo[2])

		###### Set Atlas EZO-RTD pH Sensor
		# pH has no UNIT 
	
		#TODO: Add Temperature compensation  query("T,n") 
		#TODO:  Add calibration

	except OSError as err:
		errMsg = "ERROR: No device response from ths specified address: {address} on i2cbus: {bus}]"
		errMsg = errMsg.format(bus=args.i2cbus, address=args.i2caddress)
		sys.exit(errMsg)


	time2stop = datetime.datetime.now().timestamp() + args.listentime
	while (datetime.datetime.now().timestamp() < time2stop ) or (args.listentime==-1):  # loop until time is exceeded 
		# Read Measurement from sensor
		cmdResponse = sensor.query(commands.READ)

		#format results for output
		measurement = cmdResponse.data.decode("utf-8")
		formated_measurement = ""
		timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()

		if (args.show_device_info):
			_readingtemplate='{{"timestamp":"{time}", "name":"{name}", "measurement":"{measurement}", "Device":{dev}}}'
			formated_measurement=_readingtemplate.format(time=timestamp, name=args.name, measurement=measurement, dev=deviceInfo)
		else:
			_readingtemplate='{{"timestamp":"{time}", "name":"{name}", "measurement":"{measurement}"}}'
			formated_measurement=_readingtemplate.format(time=timestamp, name=args.name, measurement=measurement)

		#publish results.
		outputter.publish(formated_measurement)

		time.sleep(args.sleeptime)

if __name__ == '__main__':
	main()

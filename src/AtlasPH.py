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

import requests   	# HTTP request NEED TO DENOTE Install PACKAGES NEEDED
import socket     	# unix socket module

import json
import os
import sys


class AtlasI2C:
	long_timeout = 2         	# the timeout needed to query readings and calibrations
	short_timeout = .5         	# timeout for regular commands
	default_bus = 1         	# the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
	default_address = 99     	# the default address for the sensor (0x63)
	current_addr = default_address

	def __init__(self, address=default_address, bus=default_bus):
		# open two file streams, one for reading and one for writing
		# the specific I2C channel is selected with bus
		# it is usually 1, except for older revisions where its 0
		# wb and rb indicate binary read and write
		self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
		self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

		# initializes I2C to either a user specified or default address
		self.set_i2c_address(address)

	def set_i2c_address(self, addr):
		# set the I2C communications to the slave specified by the address
		# The commands for I2C dev using the ioctl functions are specified in
		# the i2c-dev.h file from i2c-tools
		I2C_SLAVE = 0x703
		fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
		fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
		self.current_addr = addr

	def write(self, cmd):
		# appends the null character and sends the string over I2C
		cmd += "\00"
		self.file_write.write(cmd.encode('latin-1'))

	def read(self, num_of_bytes=31) -> string:
		# reads a specified number of bytes from I2C, then parses and displays the result
		res = self.file_read.read(num_of_bytes)         # read from the board
		if res[0] == 1: 
			# change MSB to 0 for all received characters except the first and get a list of characters
			# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
			char_list = list(map(lambda x: chr(x & ~0x80), list(res[1:])))
			
			place = 0
			for i in char_list:
				if i != "\x00":
					place = place + 1
				else:
					break
			
			char_list_edit = char_list[:-(len(char_list)-(place))]	
			value = ''.join(char_list_edit)

			#print(jsonDict)
			#print(r.text) 
			#return "Command succeeded " + ''.join(char_list)     # convert the char list to a string and returns it
			return value
		else:
			return "Error " + str(res[0])

	def query(self, string):
		# write a command to the board, wait the correct timeout, and read the response
		self.write(string)

		# the read and calibration commands require a longer timeout
		#if((string.upper().startswith("R")) or (string.upper().startswith("CAL"))):
		if(string.upper().startswith("CAL")):
			time.sleep(self.long_timeout)
		if(string.upper().startswith("R")):
			time.sleep(self.long_timeout)
		
		elif string.upper().startswith("SLEEP"):
			return "sleep mode"
		else:
			time.sleep(self.short_timeout)

		return self.read()

	def close(self):
		self.file_read.close()
		self.file_write.close()


		
def output_hec(value):
	#Using config file to setup Splunk HTTP transfers
	config = configparser.ConfigParser()
	config.read(os.path.join(sys.path[0], 'local/splunk_server.conf'))
	authHeader={'Authorization': 'Splunk '+config['DEFAULT']['token']}
	url = config['DEFAULT']['url']
	index = config['DEFAULT']['index']

  # Format and send
	jsonDict = {'host': str(socket.gethostname()), 'event': 'metric', 'index': index, 'fields':{'PH':str(value),'_value':str(value),'metric_name':'PH'}}
	r = requests.post(url,headers=authHeader,json=jsonDict,verify=False)

def output_log(logfilename:str, value: str):
	# craft filename
	today=datetime.date.today()
	logfile = logfilename + "." + str(today.year) + "." + str(today.month) + "." + str(today.day) + ".log"
	#write to file
	f = open(logfile, "a")
	f.write(value + "\n")
	f.close()

def output(args:argparse.Namespace, measurement:str="NONE", showdeviceinfo:bool=False, deviceinfo:str="NONE"):
	_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
	if (showdeviceinfo):
		_readingtemplate='{{"timestamp":"{time}", "PH":"{ph}", "Device":"{dev}"}}'
		formated_measurement=_readingtemplate.format(time=_timestamp, ph=measurement, dev=deviceinfo)
	else:
		_readingtemplate='{{"timestamp":"{time}", "PH":"{ph}"}}'
		formated_measurement=_readingtemplate.format(time=_timestamp, ph=measurement)

	# if (args.output == "LOG"):
	# 	output_log(args.logfile, formated_measurement)
	# elif (args.output == "HEC"):
	# 	output_hec(formated_measurement)
	# else: #STDOUT
	# 	print(formated_measurement)

	publish(formated_measurement)

def main():
	###### Parse Arguements
	parser = argparse.ArgumentParser(description='AtlasPH.py will poll an atlas scientific EZO-pH Temperature circuit via i2c.')
	parser.add_argument("--output", type=str, default="STDOUT", choices=list(["STDOUT","HEC","LOG"]), help="Where to output measurements: STDOUT, HEC, LOG. (Default: STDOUT)")
	parser.add_argument("--logfile", default="./AtlasPH_UF", help="Sets file path into which output measurements are appended. Only used with --output=LOG.   (Default: ./AtlasPH_UF.log)")
	#parser.add_argument("--loglevel", default="INFO", help="script logging level for messages (default: INFO) INFO, DEBUG, WARN, WARNING, ERROR")
	parser.add_argument("--listentime", type=float, default=-1, help="How the script will run (in seconds) before exiting.  (default=-1 run forever)")
	parser.add_argument("--sleeptime", type=float, default=1, help="How long to wait between measurement (in seconds) before exiting.  example: --sleeptime=.3 = 300ms (default=1s)")
	parser.add_argument("--i2cbus", type=int, default=1, help="I2C Bus Number to query [integer] (example: /dev/i2c-X)  (default=0)")
	parser.add_argument("--i2caddress", type=int, default=99, help="Device Address [integer] on the bus (example: 99 (hex 0x63) )  (default=99)")
	parser.add_argument("--show_device_info", default=False, action='store_true', help="Optional Flag: Display device info is set.")
	args=parser.parse_args()

	###### Create Atlas I2C object to read the RTD
	device_info = ""
	try:
		device = AtlasI2C(address=args.i2caddress, bus=args.i2cbus) 	# creates the I2C port object, specify the address or bus if necessary
	except FileNotFoundError as err:
		errMsg = "ERROR:  I2C bus not found.  Verify existance of: " + err.filename
		sys.exit(errMsg)

	##### Device config
	try:
		##get Atlas EZO unit info
		q = "i"
		device_info=device.query(q)
		
		#TODO: Add Temperature compensation  query("T,n") : need to get temp from Tilt?
		
		
		#TODO: Add Calibration

	except OSError as err:
		errMsg = "ERROR: No device response from ths specified address: {address} on i2cbus: {bus}]"
		errMsg = errMsg.format(bus=args.i2cbus, address=args.i2caddress)
		sys.exit(errMsg)


	###### Define graceful exit
	atexit.register(device.close)

	#Runs 1 Time and stop
	if (args.listentime==-1):
		#loop forever
		while True:
			measurement = device.query("R")
			output(args, measurement, args.show_device_info, device_info)
			time.sleep(args.sleeptime)
	else:
		time2stop = datetime.datetime.now().timestamp() + args.listentime
		
		while (datetime.datetime.now().timestamp() < time2stop):  # loop until time is exceeded 
			measurement = device.query("R")
			output(args, measurement, args.show_device_info, device_info)
			time.sleep(args.sleeptime)
	
if __name__ == '__main__':
	main()

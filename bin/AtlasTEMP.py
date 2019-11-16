#!/usr/bin/python3

import atexit     #used for graceful exit of script (close io)
import argparse   #used to parse cmdline arguements to this script
import configparser #parse config files

import io         # used to create file streams
from io import open
import fcntl      # used to access I2C parameters like addresses

import datetime   # used to form timestamp
import time       # used for sleep delay and timestamps
import string     # helps parse strings

import requests   # HTTP request NEED TO DENOTE Install PACKAGES NEEDED
import socket     # unix socket module
import os
import sys

class AtlasI2C:
	long_timeout = 2         	# the timeout needed to query readings and calibrations
	short_timeout = .5         	# timeout for regular commands
	default_bus = 1         	# the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
	default_address = 102     	# the default address for the sensor (0x66)
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
	#jsonDict = {'host': str(socket.gethostname()), 'event': 'metric', 'index': index, 'fields':{'ChamberTemp':str(value),'_value':str(value),'metric_name':'ChamberTemp'}}
	jsonDict = {'host': str(socket.gethostname()), 'event': 'metric', 'index': index, 'fields':{'ChamberTemp':str(value),'_value':str(value),'metric_name':'ChamberTemp'}}
	formated_measurement
	r = requests.post(url,headers=authHeader,json=jsonDict,verify=False)

def output_log(value: str):
	# craft filename
	today=datetime.date.today()
	logfile = logfile=args.logfile + "." + str(today.year) + "." + str(today.month) + "." + str(today.day) + ".log"
	#write to file
	f = open(get_logfile(), "a")
	f.write(msg + "\n")
	f.close()

def output(writeHere:str, measurement:str, unit:str):
	_readingtemplate='{{"timestamp":"{time}", "ChamberTemp":"{temp}", "Unit":"{unit}"}}'
	_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
	formated_measurement=_readingtemplate.format(time=_timestamp, temp=measurement, unit=unit)

	if (writeHere == "LOG"):
		output_log(formated_measurement)
	elif (writeHere == "HEC"):
		output_hec(formated_measurement)
	else: #STDOUT
		print(formated_measurement)

def main():
	###### Parse Arguements
	parser = argparse.ArgumentParser(description='AtlasTEMP.py will poll an atlas scientific RTD Temperature circuit via i2c.')
	parser.add_argument("--output", type=str, default="STDOUT", choices=list(["STDOUT","HEC","LOG"]), help="Where to output measurements: STDOUT, HEC, LOG. (Default: STDOUT)")
	parser.add_argument("--logfile", default="./AtlasTEMP_UF.log", help="Sets file path into which output measurements are appended. Only used with --output=LOG.   (Default: ./AtlasTEMP_UF.log)")
	#parser.add_argument("--loglevel", default="INFO", help="script logging level for messages (default: INFO) INFO, DEBUG, WARN, WARNING, ERROR")
	parser.add_argument("--listentime", type=int, default=-1, help="How the script will run (in seconds) before exiting.  (default=-1 run forever)")
	parser.add_argument("--sleeptime", type=float, default=1, help="How long to wait between measurement (in seconds) before exiting.  example: --sleeptime=.3 = 300ms (default=1s)")
	parser.add_argument("--i2cbus", type=int, default=0, help="I2C Bus Number to query [integer] (example: /dev/i2c-X)  (default=0)")
	parser.add_argument("--i2caddress", type=int, default=102, help="Device Address [integer] on the bus (example: 102 (hex 0x66) )  (default=102)")
	parser.add_argument("--unit", type=str, default="c", choices=(["c", "f", "k"]), help="Set temperature unit of measure celcius, fahrenheit and kelvin [values: c, f or k] (default=c)")
	args=parser.parse_args()

	###### Create Atlas I2C object to read the RTD
	device = AtlasI2C(address=AtlasI2C.default_address, bus=AtlasI2C.default_bus) 	# creates the I2C port object, specify the address or bus if necessary
	q = "S,"+ str(args.unit).upper()
	device.query(q)


	###### Define graceful exit
	atexit.register(device.close)

	#Runs 1 Time and stop
	if (args.listentime==-1):
		#loop forever
		while True:
			measurement = device.query("R")
			output(args.output, measurement, args.unit.upper())
			time.sleep(args.sleeptime)
	else:
		time2stop = datetime.datetime.now().timestamp() + args.listentime
		
		while (datetime.datetime.now().timestamp() < time2stop):  # loop until time is exceeded 
			measurement = device.query("R")
			output(args.output, measurement, args.unit)
			time.sleep(args.sleeptime)

	### output 
	

if __name__ == '__main__':
	main()

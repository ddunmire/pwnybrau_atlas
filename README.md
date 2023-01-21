# Pwnybrau_Atlas 
In the project, I am creating python scripts that makes it easier to read Atlas sensors via an I2C bus and write them to an standardout or a supported endpoint.


## Dependencies
Python Package Name | version | install | website
------------------- | ------- | ------- | -------
atlas-i2c | 0.3.1 | pip install atlas-i2c | https://pypi.org/project/atlas-i2c/ <br /> https://github.com/timboring/atlas_i2c     

## I2C validation
This project expects that sensors to be wired to an I2C bus and directly connected to the host running this code.  Below are a few steps you can take to be sure your I2C bus is mounted and working properly.

### List I2C buses
```
  $ ls -al /dev/i2c*
  output:
  crw-rw---- 1 root i2c 89, 1 Jan 19 10:20 /dev/i2c-1

```
### Probe I2C bus to see 
```
  # Probe i2c-1
  $ i2cdetect -y 1
  output:
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
  00:          -- -- -- -- -- -- -- -- -- -- -- -- --
  10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  60: -- -- -- 63 -- -- 66 -- -- -- -- -- -- -- -- --
```
Visit [Atlas Scientific](https://atlas-scientific.com/) for details on exact i2c bus addresses for your sensors.
    EZO pH Sensor defaults to 0x63 (99)
    EZO RTD Temperature defaults to   0x66 (102)


## Supported Outputs
  -**STDOUT** - sensor data is send to standard out.   

  - __LOG__ - sensor data is written to a logfile named on the cli.

  - **MQTT** - sensor measurements are published to a MQTT broker defined a config file.

  - __HEC__ - [FUTURE]  not quit ready to build this one yet.

## CLI and Sample Output
```
    $ python3 AtlasPH --name=ph --show_device_info 
    output:
      {"timestamp":"2023-01-21T02:02:18.047372+00:00", "name":"FermenterPH", "measurement":"4.509", "Device":{"type":"pH", "firmware":2.12}}

    $ python3 AtlasTemp --name=temp --show_device_info
    output:
      {"timestamp":"2023-01-21T01:56:15.094778+00:00", "name":"FermenterTemp", "measurement":"69.428", "unit":"f", "sensor":{"type":"RTD", "firmware":2.10}}
```


## Help
```
$ python3 AtlasPH.py --help
usage: AtlasPH.py [-h] [--output {STDOUT,LOG,HEC,MQTT}]
                  [--output_config OUTPUT_CONFIG] [--listentime LISTENTIME]
                  [--sleeptime SLEEPTIME] [--i2cbus I2CBUS]
                  [--i2caddress I2CADDRESS] [--show_device_info] [--name NAME]

AtlasPH.py will poll an atlas scientific EZO-pH Temperature circuit via i2c.

optional arguments:
  -h, --help            show this help message and exit
  --output {STDOUT,LOG,HEC,MQTT}
                        Where to output measurements: (Default: STDOUT)
  --output_config OUTPUT_CONFIG
                        Path and file name of the config file with our output
                        params. Used with LOG, MQTT and HEC
  --listentime LISTENTIME
                        How the script will run (in seconds) before exiting.
                        (default=-1 run forever)
  --sleeptime SLEEPTIME
                        How long to wait between measurement (in seconds)
                        before exiting. example: --sleeptime=.3 = 300ms
                        (default=1s)
  --i2cbus I2CBUS       I2C Bus Number to query [integer] (example:
                        /dev/i2c-X) (default=0)
  --i2caddress I2CADDRESS
                        Device Address [integer] on the bus (example: 99 (hex
                        0x63) ) (default=99)
  --show_device_info    Optional Flag: Display device info is set.
  --name NAME           Sensor Name.
```

## Examples
See pwnybrau_atlas/examples

### Logfile
This example outputs sensor measurements to a log file.

### Splunk Universal Forwarder (SplunkUF)
This example is a Splunk Scripted Input for a Universal Forwarder. Splunk captures sensor measurements via STDOUT and passes them to the Indexers for parsing.
Note: No props or transforms at this time.  Sorry. 



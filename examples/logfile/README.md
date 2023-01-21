#Write Sensor output to a log file
This quick example will who you how to run AtlasPH or AtlasTEMP and redirect its output to a specific file.  Each command will run for 15 seconds and publish a message approx every 3 seconds.  

##Configuration: 
**publish.conf** is a sample file.  The [LOG] stanza determine the prefix of use for the file name.  Below is a snippit:
```
[LOG]
# File prefix for sensor data.  It should be noted that [year].[month].[day] will be appended to the prefix.
# Example: logPrefix = AtlasSensors
# LogfileName: AtlasSensors.2023.01.20.log
logPrefix = AtlasSensors  
```

##Running the script
```
$ python3 AtlasPH.py --output=LOG --output_config=publish.conf --listentime=15 --sleeptime=3

$ python3 AtlasTEMP.py --output=LOG --output_config=publish.conf --listentime=15 --sleeptime=3
```


**Remember:** AtlasPH.py and AtlasTEMP.py can bother be run using the `--help` for more information 


##Next steps:
1. You could use CRON or similar to continuously write to a file.  Each day the file would roll over.  
1. Send the data someplace nice.  Use a SPLUNK UF to monitor the folder and ingest each of these logs. 
1. Dont forget to clean up your log pile, or the drive will fill up.
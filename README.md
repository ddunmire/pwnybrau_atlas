# Pwnybrau_Atlas 
In the project, I am creating python scripts that makes it easier to read Atlas sensors via an I2C bus and write them to an standardout or a supported endpoint.


## Dependencies
Python Package Name | version | install | website
------------------- | ------- | ------- | -------
atlas-i2c | 0.3.1 | pip install atlas-i2c | https://pypi.org/project/atlas-i2c/ <br /> https://github.com/timboring/atlas_i2c     



## Suported Endpoints
__stdout__ - just dump output to standard out.   
__LogFile__ - dump output to a logfile named on the cli


## Example Usage
### Splunk Universal Forwarder
The Splunk UF implementation could be done 2 ways.  
1. Splunk UF ModInput to trigger the script and then process stdout.
2. Tail log file - set up cron job or use systemd to run the script as a service where output is written to a log file.  Then Splunk UF could tail that file.



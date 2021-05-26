# Follw.app Remote Device Python client

A Python 3 client for retrieving your device location from the device tracking platforms Apple Find My and Prey Project and sharing it to the Follw.app WebService

## About Follw.app
Follw.app is a privacy focused location sharing service. Only a unique Sharing ID and derived Sharing URL is given and no account details, user credentials, IP addresses, Cookies and other sensitive information are used or stored on the Follw.app servers.

Whenever a new location is submitted the previous location is overwritten, no location history is stored.

Whenever you delete your unique Sharing ID all location details are removed from the Follw.app servers. Only a hash of your Sharing ID is stored after removal to guarantee a Sharing ID is not reassigned again.

## Location retrieval
The Follw.app Remote Device Python client authenticates with a device tracking platform and tries to retrieve your device location. When successfull it then submits this location to the Follw.app webservice.

When no device ID or name is given the available device IDs and names for the selected service are retrieved and listed and the client will exit

**Follw.app can not guarantee your privacy when using a third party device tracking platform**

## Usage

The Follw.app Python client is written in Python 3, you need a Python 3 interpreter to run this software. How to install Python 3 on your specific Operating System is not in the scope of this document.

```
usage: FollwDevice [-h] [-f] [--oneshot] [-i INTERVAL] --platform {apple,prey} [--username USERNAME] [--password PASSWORD] [--apikey APIKEY] [--deviceid DEVICEID]
                   [--devicename DEVICENAME] [--debug]
                   url

positional arguments:
  url                   your unique Follw.app sharing URL

optional arguments:
  -h, --help            show this help message and exit
  -f, --foreground      run process in the foreground
  --oneshot             submit location only once and exit
  -i INTERVAL, --interval INTERVAL
                        logging interval in seconds (default: 5)
  --platform {apple,prey}
                        the device tracking platform
  --username USERNAME   the username for the selected device tracking platform
  --password PASSWORD   the password for the selected device tracking platform
  --apikey APIKEY       the API key for the selected device tracking platform
  --debug               Show debugging messages

  --deviceid DEVICEID, --id DEVICEID
                        The id of the device
  --devicename DEVICENAME, --name DEVICENAME
                        The name of the device
```

### Apple Find My
User your iCloud email address and password for authentication

To get a list of available devices

`python3 FollwDevice --platform apple --username USERNAME --password PASSWORD`

To retrieve a location for a specific device and post the location to Follw.app

`python3 FollwDevice --platform apple --username USERNAME --password PASSWORD --deviceid DEVICEID url`

or

`python3 FollwDevice --platform apple --username USERNAME --password PASSWORD --devicename DEVICENAME url`

### Prey
Create a Prey API Key at `https://panel.preyproject.com/login`

To get a list of available devices

`python3 FollwDevice --platform prey --apikey APIKEY`

To retrieve a location for a specific device and post the location to Follw.app

`python3 FollwDevice --platform prey --apikey APIKEY --deviceid DEVICEID url`

or

`python3 FollwDevice --platform prey --apikey APIKEY --devicename DEVICENAME url`
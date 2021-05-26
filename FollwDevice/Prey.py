import logging, time, json, urllib, socket
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Prey():
  terminate = False
  online = True

  apikey = None
  deviceId = None
  deviceName = None

  baseURL = 'https://api.preyproject.com/v1'

  interval = 5
  lastLookup = 0

  location = None
  # timestamp = time.time()
  timestamp = 0
  
  def stop(self):
    self.terminate = True

  def online(self, online = True):
    self.online = online

  def offline(self, offline = True):
    self.online = not offline

  def getLocation(self):
    if not self.online:
      return None

    elapsedTime = time.time() - self.lastLookup
    if elapsedTime < self.interval:
      return None

    location = None

    headers = {
      'apikey': self.apikey
    }

    url = self.baseURL + '/devices'
    try:
      request = urllib.request.Request(url, headers=headers)
      with urllib.request.urlopen(request, timeout=10) as response:
        responseData = response.read().decode(response.headers.get_content_charset(failobj = 'utf-8'))
        responseData = json.loads(responseData)

        for device in responseData['devices']:
          if not self.deviceId and not self.deviceName:
            logger.info("{} - {}".format(device['id'], device['name']))
          elif self.deviceId and device['id'] == self.deviceId:
            self.deviceName = device['name']
            break
          elif self.deviceName and device['name'] == self.deviceName:
            self.deviceId = device['id']
            break
    except urllib.error.HTTPError as e:
      if e.code == 404:
        logger.warning("No location found for {}".format(url))
      else:
        logger.error(e.code)
        return None
    except urllib.error.URLError as e:
      logger.error(e)
      return None
    except socket.timeout as e:
      logger.error(e)
      return None

    if not self.deviceId and not self.deviceName:
      return None

    if not self.deviceName:
      logger.error("No device found with ID {}".format(self.deviceId))
      return None
    if not self.deviceId:
      logger.error("No device found with name \"{}\"".format(self.deviceName))
      return None
    
    url = '{}/devices/{}/location_activity'.format(self.baseURL, self.deviceId)
    try:
      request = urllib.request.Request(url, headers=headers)
      with urllib.request.urlopen(request, timeout=10) as response:
        responseData = response.read().decode(response.headers.get_content_charset(failobj = 'utf-8'))
        responseData = json.loads(responseData)

        # location = None
        if len(responseData['latest_locations']) > 0:
          latitude = responseData['latest_locations'][0]['lat']
          longitude = responseData['latest_locations'][0]['lng']
          accuracy = responseData['latest_locations'][0]['accuracy']
          timestamp = responseData['latest_locations'][0]['created_at']
          timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
          timestamp = timestamp.timestamp()
          location = [latitude, longitude, accuracy]
        else:
          logger.error("No location found in device {} \"{}\"".format(self.deviceId, self.deviceName))
          logger.debug(responseData)
    except urllib.error.HTTPError as e:
      if e.code == 404:
        logger.warning("Device {} \"{}\" not found".format(self.deviceId, self.deviceName))
      else:
        logger.error(e.code)
        return None
    except urllib.error.URLError as e:
      logger.error(e)
      return None
    except socket.timeout as e:
      logger.error(e)
      return None

    self.lastLookup = time.time()

    if location and timestamp != self.timestamp:
      logger.debug(location)
      self.location = location
      self.timestamp = timestamp
      return location
    
    return None
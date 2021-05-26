import logging, time, json, urllib, socket
from http.cookiejar import MozillaCookieJar

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GoogleFindMyDevice():
  terminate = False
  online = True

  username = None
  Password = None
  deviceId = None
  deviceName = None

  cookiejar = MozillaCookieJar()
  
  loggedin = False
  
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

  def login(self):
    if not self.online:
      return False

    url = ''.format()

    headers = {
    }
    
    requestData = ''
    requestData = requestData.encode('utf-8')
    
    try:
      opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
      urllib.request.install_opener(opener)
      request = urllib.request.Request(url, requestData, headers)
      with urllib.request.urlopen(request, timeout=5) as response:
        responseData = response.read().decode(response.headers.get_content_charset(failobj = 'utf-8'))
        logger.debug(responseData)
        # responseData = json.loads(responseData)
    except urllib.error.HTTPError as e:
      logger.error(e.code)
      return False
    except urllib.error.URLError as e:
      logger.error(e)
      return False
    except socket.timeout as e:
      logger.error(e)
      return False
    
    self.loggedin = True
    return True

  def getLocation(self):
    if not self.online:
      return None

    # if not self.loggedin and not self.login():
    #   return None

    elapsedTime = time.time() - self.lastLookup
    if elapsedTime < self.interval:
      return None

    location = None
# curl 'https://maps.googleapis.com/maps/api/js/GeocodeService.Search?5m2&1d52.3660285&2d4.8502509&7sUS&9snl&callback=_xdc_._144ct4&client=google-nova&token=26111' \
#   -H 'authority: maps.googleapis.com' \
#   -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"' \
#   -H 'dnt: 1' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36' \
#   -H 'accept: */*' \
#   -H 'x-client-data: CKG1yQEIlbbJAQijtskBCMG2yQEIqZ3KAQj4x8oBCMvZygEIqJ3LAQigoMsBCNzyywEIqPPLARiOnssB' \
#   -H 'sec-fetch-site: cross-site' \
#   -H 'sec-fetch-mode: no-cors' \
#   -H 'sec-fetch-dest: script' \
#   -H 'referer: https://www.google.com/' \
#   -H 'accept-language: en-NL,en;q=0.9,nl-NL;q=0.8,nl;q=0.7,en-US;q=0.6' \
#   --compressed
    url = 'https://maps.googleapis.com/maps/api/js/GeocodeService.Search?5m2&1d52.3660285&2d4.8502509&7sUS&9snl&callback=_xdc_._144ct4&client=google-nova&token=26111'

    headers = {
      'authority': 'maps.googleapis.com',
      'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
      'dnt': '1',
      'sec-ch-ua-mobile': '?0',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
      'accept': '*/*',
      'x-client-data': 'CKG1yQEIlbbJAQijtskBCMG2yQEIqZ3KAQj4x8oBCMvZygEIqJ3LAQigoMsBCNzyywEIqPPLARiOnssB',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-mode': 'no-cors',
      'sec-fetch-dest': 'script',
      'referer': 'https://www.google.com/',
      'accept-language': 'en-NL,en;q=0.9,nl-NL;q=0.8,nl;q=0.7,en-US;q=0.6'
    }

    requestData = '{}'
    requestData = bytes(requestData, 'utf-8')
    # logger.debug(requestData)

    try:
      opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
      urllib.request.install_opener(opener)
      request = urllib.request.Request(url, requestData, headers)
      with urllib.request.urlopen(request, timeout=1) as response:
        responseData = response.read().decode(response.headers.get_content_charset(failobj = 'utf-8'))
        responseData = responseData[responseData.index('{'):responseData.index(')')]
        logger.debug(responseData)
        responseData = json.loads(responseData)
        #logger.debug(responseData)
 
        # if device and 'location' in device and device['location']:
        #   logger.debug(device)
        #   latitude = None
        #   longitude = None
        #   accuracy = None
        #   altitude = None
        #   timestamp = None
        #   location = [latitude, longitude, accuracy, altitude]
        #   logger.debug(location)
        # else:
        #   logger.error("No location found")
        #   logger.debug(device)
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

    self.lastLookup = time.time()

    if location and timestamp != self.timestamp:
      logger.debug(timestamp - self.timestamp)
      self.location = location
      self.timestamp = timestamp
      return location
    
    return None
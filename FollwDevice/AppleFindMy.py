import os, logging, time, json, urllib, socket
from http.cookiejar import MozillaCookieJar

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AppleFindMy():
  terminate = False
  online = True

  username = None
  password = None
  deviceId = None
  deviceName = None

  cookiejar = None
  
  loggedin = False
  findmeBaseURL = None
  serverContext = None
  
  interval = 5
  lastLookup = 0

  def __init__(self):
    self.cookiejar = MozillaCookieJar(os.path.dirname(os.path.realpath(__file__)) + '/../.cookies.txt')
    try:
      self.cookiejar.load()
    except OSError as e:
      if e.errno == 2:
        self.cookiejar.save()
      else:
        logger.error(e)

  def stop(self):
    self.terminate = True

  def online(self, online = True):
    self.online = online

  def offline(self, offline = True):
    self.online = not offline

  def login(self):
    if not self.online:
      return False

    url = 'https://setup.icloud.com/setup/ws/1/accountLogin'

    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
      'Content-Type': 'text/plain;charset=UTF-8',
      'Accept': '*/*',
      'Origin': 'https://www.icloud.com',
      'Referer': 'https://www.icloud.com/',
      'Accept-Language': 'en-UK,en;q=0.9,en-US;q=0.8'
    }
    
    requestData = '{"appName":"find","apple_id":"' + self.username + '","password":"' + self.password + '"}'
    requestData = requestData.encode('utf-8')
    
    try:
      opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
      urllib.request.install_opener(opener)
      request = urllib.request.Request(url, requestData, headers)
      with urllib.request.urlopen(request, timeout=5) as response:
        responseData = response.read().decode(response.headers.get_content_charset(failobj = 'utf-8'))
        # logger.debug(responseData)
        responseData = json.loads(responseData)
        self.findmeBaseURL = responseData['webservices']['findme']['url']
        
        self.cookiejar.save()
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
    
    if not self.loggedin and not self.login():
      return None

    elapsedTime = time.time() - self.lastLookup
    if elapsedTime < self.interval:
      return None

    location = None

    url = self.findmeBaseURL + '/fmipservice/client/web/refreshClient'

    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
      'Content-Type': 'text/plain',
      'Accept': '*/*',
      'Origin': 'https://www.icloud.com',
      'Referer': 'https://www.icloud.com/',
      'Accept-Language': 'en-UK,en;q=0.9,en-US;q=0.8'
    }

    requestData = {}
    if(self.serverContext):
      requestData['serverContext'] = self.serverContext
    requestData['clientContext'] = json.loads('{"appName":"iCloud Find (Web)","appVersion":"2.0","timezone":"Europe/Amsterdam","inactiveTime":2,"apiVersion":"3.0","deviceListVersion":1,"fmly":true,"shouldLocate":true}')
    if(self.deviceId):
      requestData['clientContext']['selectedDevice'] = self.deviceId
    else:
      requestData['clientContext']['selectedDevice'] = 'all'
    requestData = json.dumps(requestData)
    requestData = bytes(requestData, 'utf-8')
    # logger.debug(requestData)

    try:
      opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
      urllib.request.install_opener(opener)
      request = urllib.request.Request(url, requestData, headers)
      with urllib.request.urlopen(request, timeout=1) as response:
        responseData = response.read().decode(response.headers.get_content_charset(failobj = 'utf-8'))
        # logger.debug(responseData)
        responseData = json.loads(responseData)
        self.serverContext = responseData['serverContext']

        for device in responseData['content']:
          if not self.deviceId and not self.deviceName:
            logger.info("{} - {}".format(device['id'], device['name']))
          elif self.deviceId and device['id'] == self.deviceId:
            break
          elif self.deviceName and device['name'] == self.deviceName:
            break
          device = None

        if not self.deviceId and not self.deviceName:
          return None
        if not device:
          logger.error("No device found")
          return None

        if device and 'location' in device and device['location']:
          latitude = device['location']['latitude']
          longitude = device['location']['longitude']
          accuracy = device['location']['horizontalAccuracy']
          altitude = device['location']['altitude']
          location = [latitude, longitude, accuracy, altitude]
          # logger.debug(location)
        else:
          logger.error("No location found in device {} \"{}\"".format(device['id'], device['name']))
          logger.debug(device)

        self.cookiejar.save()
    except urllib.error.HTTPError as e:
      if e.code == 404:
        logger.warning("Not found {}".format(url))
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

    return location
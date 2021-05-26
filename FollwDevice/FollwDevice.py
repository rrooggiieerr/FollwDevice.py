import logging, time, urllib.request, urllib.parse, socket
from AppleFindMy import AppleFindMy
from Prey import Prey

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FollwDevice:
  platforms = {
    'apple': AppleFindMy,
    'prey': Prey
  }

  terminate = False
  url = None
  interval = 5
  oneshot = False
  online = True

  location = None

  def __init__(self, platform):
    self.location = self.platforms[platform]()

  def stop(self):
    """ Stop the Follw process """
    logger.info("Stopping Follw")
    self.terminate = True
    self.location.stop()

  def online(self, online = True):
    self.online = online

  def offline(self, offline = True):
    self.online = not offline

  def run(self):
    """ The main loop of the Follw process """
    previousLocation = None
    _time = time.time()
    while not self.terminate:
      location = None

      elapsedTime = time.time() - _time
      if not previousLocation or elapsedTime > self.interval:
        location = self.location.getLocation()

        if location and location != previousLocation:
          logger.debug(location)
          if previousLocation:
            logger.debug("{} seconds since last submit".format(elapsedTime))
          if self.submitLocation(*location):
            previousLocation = location
            _time = time.time()

        if self.oneshot:
          break
      time.sleep(0.1)

    if self.terminate:
      logger.info("Stopped Follw")

  def submitLocation(self, latitude, longitude, accuracy = None, altitude = None, direction = None, speed = None):
    parsedUrl = urllib.parse.urlparse(self.url)

    if not self.online:
      return False

    url = parsedUrl.scheme
    url += "://"
    url += parsedUrl.netloc
    if parsedUrl.path:
      url += parsedUrl.path
    else:
      url += "/"
    url += "?"
    if parsedUrl.query:
      url += parsedUrl.query
      url += "&"
    url += 'la={}&lo={}'.format(latitude, longitude)
    if accuracy:
      url += '&ac={}'.format(accuracy)
    if altitude:
      url += '&al={}'.format(altitude)
    if direction:
      url += '&di={}'.format(direction)
    if speed:
      url += '&sp={}'.format(speed)
    logger.debug(url);

    try:
      urllib.request.urlopen(url, timeout=1)

      logger.info("Submitted location {},{}".format(latitude, longitude))
      return True
    except urllib.error.HTTPError as e:
      if e.code == 404:
        logger.error("Follw share ID does not exist")
        self.terminate = True
      elif e.code == 410:
        logger.error("Follw share ID is deleted")
        self.terminate = True
      else:
        logger.error(e.code)
        logger.error(e.reason)
    except urllib.error.URLError as e:
      logger.error(e.reason)
    except socket.timeout as e:
      logger.error(e)

    return False
import os, sys, logging, signal, argparse, urllib.parse

from FollwDevice import FollwDevice

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def daemonize():
  # Example code from https://gist.github.com/slor/5946334

  # fork 1 to spin off the child that will spawn the daemon
  if os.fork():
    sys.exit()

  # This is the child.
  # 1. cd to root for a guarenteed working dir
  # 2. clear the session id to clear the controlling TTY
  # 3. set the umask so we have access to all files created by the daemon
  os.chdir("/")
  os.setsid()
  os.umask(0)

  # fork 2 ensures we can't get a controlling ttd.
  if os.fork():
    sys.exit()

  # This is a child that can't ever have a controlling TTY.
  # Now we shut down stdin and point stdout/stderr at log files.

  # stdin
  with open('/dev/null', 'r') as dev_null:
    os.dup2(dev_null.fileno(), sys.stdin.fileno())

# Custom argparse validator for URLs
def url(value):
  parsedUrl = urllib.parse.urlparse(value)
  if parsedUrl.scheme and parsedUrl.netloc:
    return value

  raise argparse.ArgumentTypeError("%s is an invalid URL" % value)

class IntRange:
  def __init__(self, min=None, max=None):
    self.min = min
    self.max = max

  def __call__(self, arg):
    try:
      value = int(arg)
    except ValueError:
      raise argparse.ArgumentTypeError("Must be an integer")

    if (self.min is not None and value < self.min):
      raise argparse.ArgumentTypeError("Must be an integer >= {}".format(self.min))
    if (self.max is not None and value > self.max):
      raise argparse.ArgumentTypeError("Must be an integer <= {}".format(self.max))

    return value

def main():
  # Read command line arguments
  argparser = argparse.ArgumentParser()
  argparser.add_argument('url', type=url, nargs='?', help="your unique Follw.app sharing URL")
  argparser.add_argument('-d', '--daemon', dest='daemon', action='store_const', const=True, default=False, help="run process as a daemon in the background")
  argparser.add_argument('--oneshot', dest='oneshot', action='store_const', const=True, default=False, help="submit location only once and exit")
  argparser.add_argument('-i', '--interval', dest='interval', type=IntRange(0), default=FollwDevice.interval, help="logging interval in seconds (default: %(default)s)")
  argparser.add_argument('--platform', dest='platform', choices=FollwDevice.platforms.keys(), required=True, help="the device tracking platform")
  argparser.add_argument('--username', dest='username', default=None, help="the username for the selected device tracking platform")
  argparser.add_argument('--password', dest='password', default=None, help="the password for the selected device tracking platform")
  argparser.add_argument('--apikey', dest='apikey', default=None, help="the API key for the selected device tracking platform")
  group = argparser.add_argument_group()
  group.add_argument('--deviceid', '--id', dest='deviceId', default=None, help="The id of the device")
  group.add_argument('--devicename', '--name', dest='deviceName', default=None, help="The name of the device")
  argparser.add_argument('--debug', dest='debug', action='store_const', const=True, default=False, help="Show debugging messages")
  args = argparser.parse_args()

  if args.platform == 'apple' and not args.username:
    argparser.error("username required for Apple platform")
  if args.platform == 'apple' and not args.password:
    argparser.error("password required for Apple platform")

  if args.platform == 'prey' and not args.apikey:
    argparser.error("API key required for Prey platform")

  if not args.deviceId and not args.deviceName:
    args.oneshot = True

  daemon = False
  if args.daemon and not args.oneshot:
    daemon = True

  if daemon:
    logging.basicConfig(filename=os.path.dirname(os.path.realpath(__file__)) + '/../log.txt', format='%(asctime)s %(levelname)-8s %(name)s.%(funcName)s() %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  else:
    logging.basicConfig(format='%(levelname)-8s %(message)s')
    stdoutHandler = logging.StreamHandler(sys.stdout)
    stdoutHandler.setLevel(logging.DEBUG)
    if not args.debug:
      logging.disable(logging.DEBUG)
    stdoutHandler.addFilter(lambda record: record.levelno <= logging.INFO)
    stderrHandler = logging.StreamHandler(sys.stderr)
    stderrHandler.setLevel(logging.WARNING)
    logger.addHandler(stdoutHandler)
    logger.addHandler(stderrHandler)

  print(os.path.dirname(os.path.realpath(__file__)))
  follw = FollwDevice(args.platform)
  signal.signal(signal.SIGINT, follw.stop)
  signal.signal(signal.SIGTERM, follw.stop)

  follw.oneshot = args.oneshot
  follw.interval = args.interval

  follw.location.username = args.username
  follw.location.password = args.password
  follw.location.apikey = args.apikey
  follw.location.deviceId = args.deviceId
  follw.location.deviceName = args.deviceName

  # URL is validated by argparse
  follw.url = args.url

  if not follw.oneshot:
    logger.info("Starting FollwDevice")

  if not args.deviceId and not args.deviceName:
    logger.info("No device ID or name are given, will display all device IDs and names and exiting")

  if daemon:
    daemonize()
    follw.run()
  else:
    try:
      follw.run()
    except (KeyboardInterrupt):
      follw.stop()

if __name__ == '__main__':
  main()
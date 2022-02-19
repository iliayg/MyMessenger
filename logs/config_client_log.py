import sys
import os
import logging
import logging.handlers
from common.variables import LOGGING_LEVEL
sys.path.append('../')


# logs formatter
CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s', datefmt='%Y-%m-%d,%H:%M:%S\n')
# logs filename preparing
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')
# create log stream
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(CLIENT_FORMATTER)
# create logger and set up
LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)
# debugging
if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug')
    LOGGER.info('Info')
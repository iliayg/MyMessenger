import logging


DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
LOGGING_LEVEL = logging.DEBUG  # current logging level

# JIM protocol general keys
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# other keys used in protocol
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'm'
MESSAGE_TEXT = 'message_text'
EXIT = 'q'

# dictionaries - responses
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {RESPONSE: 400}
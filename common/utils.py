import sys
import json
import logging
import logs.config_utils_log
from common.variables import MAX_PACKAGE_LENGTH, ENCODING, ERROR
from decorators import log
from errors import IncorrectDataReceivedError, NonDictInputError
sys.path.append('../')

# utils log initialization
LOGGER = logging.getLogger('utils')


@log
def get_message(client):
    """
    utlility for receiving and decoding messages

    receives bytes and returns dictionary, else returns error
    """
    # LOGGER.debug(f"\nChecking client message: '{client}'")
    encoded_responce = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_responce, bytes):
        json_response = encoded_responce.decode(ENCODING)
        response = json.loads(json_response)

        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataReceivedError

    else:
        raise IncorrectDataReceivedError


@log
def send_message(sock, message):
    """
    utility for encoding and sending a message

    receives dictionary and sends it
    """
    if not isinstance(message, dict):
        raise NonDictInputError

    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
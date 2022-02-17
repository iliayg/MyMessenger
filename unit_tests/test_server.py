import sys
import os
import unittest

from common.variables import RESPONSE, ERROR, USERNAME, TIME, ACTION, PRESENCE
from server import process_client_message
sys.path.append(os.path.join(os.getcwd(), '..'))


class TestServer(unittest.TestCase):
    """there is only one test-function th server"""
    err_dict = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }
    ok_dict = {RESPONSE: 200}

    def test_no_action(self):
        pass
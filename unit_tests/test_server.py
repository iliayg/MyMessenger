from time import time
import unittest
from unittest import TestCase
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
import server
from server import process_client_message
# from server import main, messages_list, client, clients, names


class TestServer(TestCase):
    def setUp(self, account_name=None) -> None:
        self.dict_no_action = {TIME: time(), USER: {ACCOUNT_NAME: account_name}}
        self.dict_no_time = {ACTION: PRESENCE,
                             USER: {ACCOUNT_NAME: account_name}}
        self.dict_no_user = {ACTION: PRESENCE, TIME: time()}
        self.response_ok = {RESPONSE: 200}
        self.response_error = {RESPONSE: 400, ERROR: 'Bad Request'}


    def test_no_action(self):
        """error if there is no action"""
        self.assertEqual(process_client_message(self.dict_no_action), self.response_error)

    def test_wrong_action(self):
        """if there is wrong action"""
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_time(self):
        """if there is no time field"""
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    def test_no_user(self):
        """there is no user"""
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1}), self.err_dict)

    def test_unknown_user(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.err_dict)

    def test_ok_check(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)


if __name__ == '__main__':
    unittest.main()
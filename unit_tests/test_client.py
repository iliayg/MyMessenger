# import sys
import os
import unittest
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_response, ReqFieldMissingError, ServerError
# sys.path.append(os.path.join(os.getcwd(), '..'))


class TestClass(unittest.TestCase):
    def test_def_presence(self):
        """test for correct request"""
        test = create_presence('Guest')
        test[TIME] = 1.1  # must to equalize the time, else test will never be passed
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME:'Guest'}})

    def test_200_ans(self):
        """test for response 200 correct analize"""
        self.assertEqual(process_response({RESPONSE: 200}), '200:OK')

    def test_400_ans(self):
        # self.assertEqual(process_response({RESPONSE: 400, ERROR: 'Bad request'}), '400: Bad request')
        self.assertRaises(ServerError, process_response, {RESPONSE: 400, ERROR:'Bad request'})

    def test_no_response(self):
        """exception without RESPONSE field test"""
        self.assertRaises(ReqFieldMissingError, process_response, {ERROR:'Bad request'})


if __name__ == "__main__":
    unittest.main()
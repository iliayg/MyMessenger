from time import time
import unittest
from unittest import TestCase
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, \
    SENDER, PRESENCE, ERROR, MESSAGE, MESSAGE_TEXT, RESPONSE_400, RESPONSE_200, DESTINATION, EXIT, RESPONSE
from server import process_client_message, arg_parser
import subprocess
from itertools import cycle
from common.utils import get_message, send_message
import socket
import select


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогонятся
    через тестовую функцию
    """
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_to_send):
        """
        Тестовая функция отправки, корретно  кодирует сообщение,
        так-же сохраняет что должно было отправлено в сокет.
        message_to_send - то, что отправляем в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # кодирует сообщение
        self.encoded_message = json_test_message.encode(ENCODING)
        # сохраняем что должно было отправлено в сокет
        self.receved_message = message_to_send

    def recv(self, max_len):
        """
        Получаем данные из сокета
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestServer(TestCase):

    names_count = 0
    process = []
    while True:
        action = input('Press "Enter" to start or "q" to quit:')
        if action == 'q':
            break
        else:
            process.append(subprocess.Popen('gnome-terminal -- python3 server.py', shell=True))

            for el in cycle('ab'):
                if names_count == 2:
                    break
                process.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n {el}', shell=True))
                names_count += 1



    def setUp(self, account_name=None) -> None:

        self.dict_no_action = {TIME: time(), USER: {ACCOUNT_NAME: account_name}}
        self.dict_no_time = {ACTION: PRESENCE,
                             USER: {ACCOUNT_NAME: account_name}}
        self.dict_no_user = {ACTION: PRESENCE, TIME: time()}
        test_dict_recv_ok = {RESPONSE: 200}
        test_dict_recv_err = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

        listen_address, listen_port = arg_parser()
        # preparing socket
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))
        transport.settimeout(0.5)
        # client list
        self.clients = []
        # messages queue
        self.messages = []
        # users dict
        self.names = dict()
        # listening port
        transport.listen(MAX_CONNECTIONS)

        # program main cycle
        while True:
            # wait for connection, if time ended get exception
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                self.clients.append(client)

            self.recv_data_list = []
            send_data_list = []
            err_list = []
            # check for waiting clients existence
            try:
                if self.clients:
                    recv_data_list, send_data_list, err_list = select.select(self.clients, self.clients, [])
            except OSError:
                pass

    def test_no_action(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(process_client_message(
            test_sock_ok, self.messages, self.dict_no_action, self.clients, self.names), self.test_dict_recv_err)

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
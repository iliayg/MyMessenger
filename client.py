import sys
import socket
import argparse
import logging
import logs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, \
    RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import get_message, send_message
from decorators import log
from errors import IncorrectDataReceivedError, ReqFieldMissingError, ServerError
import json
import time
import threading

# client log initialization
LOGGER = logging.getLogger('client')
fmtime = time.strftime("%H:%M:%S")


@log
def create_exit_message(account_name):
    """create dictionary with notification of exit"""
    return {
        ACTION: EXIT,
        TIME: time.strftime("%H:%M:%S"),
        ACCOUNT_NAME: account_name
    }


@log
def message_from_server(sock, my_username):
    """message handler for received messages"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message and \
                    MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f"\nReceived message from user {message[SENDER]}:\n'{message[MESSAGE_TEXT]}'")
                LOGGER.info(f"\nReceived message from user '{message[SENDER]}':\n'{message[MESSAGE_TEXT]}'")
            else:
                LOGGER.error(f"\nIncorrect message received from server: '{message}'.")
        except IncorrectDataReceivedError:
            LOGGER.exception(f'\nUnable to decode the received message.')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            LOGGER.exception(f'\nLost connection to the server.')
            break


@log
def create_message(sock, account_name='Guest'):
    """request and send a message and a receiver name to the server"""
    receiver = input('Receiver: ')
    message = input('Message: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: receiver,
        TIME: time.strftime("%H:%M:%S"),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'\nMessage dictionary formed: {message_dict}.')
    try:
        send_message(sock, message_dict)
        LOGGER.info(f"\nMessage sent to user: '{receiver}'.")
    except:
        LOGGER.exception('\nLost connection to the server.')
        sys.exit(1)


@log
def user_interface(sock, username):
    """UI gets commands from the user and sends them to the server"""
    print_help()
    while True:
        command = input('Enter command: ')
        if command == 'm':
            create_message(sock, username)
        elif command == 'h':
            print_help()
        elif command == 'q':
            send_message(sock, create_exit_message(username))
            print("Disconnection...")
            LOGGER.info("\nUser has cancelled the chat.")
            # time delay for disconnection message
            time.sleep(0.1)
            break
        else:
            print('Unknown command.')


@log
def create_presence(account_name):
    """generate request about client presence"""
    output = {ACTION: PRESENCE,
              TIME: time.strftime("%H:%M:%S"),
              USER: {
                  ACCOUNT_NAME: account_name}}
    LOGGER.debug(f"\nGenerated {PRESENCE} message for the user '{account_name}'.")
    return output


def print_help():
    """presentation of commands list"""
    print('Supported commands:')
    print('m - send message')
    print('h - show this help list')
    print('q - quit')


@log
def process_response(message):
    """detect server response about connectivity"""
    LOGGER.debug(f"\nServer welcome message verification: {message}")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200:OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400:{message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def client_arg_parser() -> object:
    """CLI arguments parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    username = namespace.name
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f"\nClient attempts to connect to wrong port: '{server_port}'."
            f" Available ports are '{1024 - 65535}'. Closing connection."
        )
        sys.exit(1)
    return server_address, server_port, username


def main():
    print('Console messenger. Client module.')
    # CLI parameters load
    server_address, server_port, username = client_arg_parser()
    # request the name if client name wasn't adjusted
    if not username:
        username = input('Please enter your name: ')
    LOGGER.info(
        f"\nClient has launched on server: '{server_address}', port: '{server_port}', username: '{username}'."
    )
    # socket initialization and notifying the server about presense
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(username))
        answer = process_response(get_message(transport))
        LOGGER.info(f"\nUser '{username}' has established connection with a server. Response from server: {answer}.")
        print(f'Hello "{username}"! You are now connected to the server.')

    except json.JSONDecodeError:
        LOGGER.exception('\nJSON string decoding failed.')
        sys.exit(1)

    except ServerError as error:
        LOGGER.exception(f'\nServer has returned a connection error: {error.text}.')
        sys.exit(1)

    except ReqFieldMissingError as missing_field_error:
        LOGGER.exception(f"\nMissing field in server response '{missing_field_error.missing_field}'.")
        sys.exit(1)

    except (ConnectionRefusedError, ConnectionError):
        LOGGER.exception(
            f'\nConnection to the server {server_address}:{server_port} has failed, host refused to connect.')
        sys.exit(1)

    # if connection established launch client-side receiving thread
    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, username))
        receiver.daemon = True
        receiver.start()
        # then start sending and interaction thread
        UI = threading.Thread(target=user_interface, args=(transport, username))
        UI.daemon = True
        UI.start()
        LOGGER.debug('\nThreads started.')
        # Watchdog - main cycle, if one of the threads ended - it means lost connection or user gave command "exit"
        while True:
            time.sleep(1)
            if receiver.is_alive() and UI.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
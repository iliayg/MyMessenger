import sys
import socket
import argparse
import logging
import select
import logs.config_server_log
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, \
    SENDER, PRESENCE, ERROR, MESSAGE, MESSAGE_TEXT, RESPONSE_400, RESPONSE_200, DESTINATION, EXIT
from decorators import log
from common.utils import get_message, send_message

# server log initialization
LOGGER = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names):
    """gets and checks dict - client message"""
    LOGGER.debug(f'\nChecking client message: {message} \n{client}')
    # if this is presence notification - gets and answers
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        # if user is registered send message and close connection, else register him
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'This name is already used. '
            send_message(client, response)
            clients.remove(client)
            client.close()
            return
    # if it is message add it to queue, no need for answer
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message and \
            SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # if client exit
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        print(message[TIME])
        print(f"User '{message[ACCOUNT_NAME]}' has left the chat.")
        clients.remove(names[MESSAGE[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # else "Bad request"
    else:
        response = RESPONSE_400
        response[ERROR] = 'Bad request.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    message addresation to the specified client

    gets message-dictionary, list of registered users and listening ports
    does not return anything
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        LOGGER.error(f"\nUser '{message[DESTINATION]}' is not registered in the server, sending failed.")


@log
def arg_parser():
    """CLI arguments parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'\nClient attempts to connect to wrong port: {listen_port}.'
            f'Enabled ports are 1024 - 65535. Closing connection.'
        )
        sys.exit(1)
    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()
    LOGGER.info(f'\nServer started, listening port: {listen_port}, listening address:{listen_address}.')
    # preparing socket
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    # client list
    clients = []
    # messages queue
    messages = []
    # users dict
    names = dict()
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
            LOGGER.info(f'\nEstablished connection with client: {client_address}.')
            clients.append(client)

        recv_data_list = []
        send_data_list = []
        err_list = []
        # check for waiting clients existence
        try:
            if clients:
                recv_data_list, send_data_list, err_list = select.select(clients, clients, [])
        except OSError:
            pass

        # receive the message, if error - remove the client
        if recv_data_list:
            for client_with_message in recv_data_list:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except Exception:
                    LOGGER.info(f'\nClient {client_with_message.getpeername()} disconnected from server.')
                    clients.remove(client_with_message)
        # if messages exist handle everyone
        for i in messages:
            try:
                process_message(i, names, send_data_list)
                print(f'({i[TIME]}) {i[SENDER]}:"{i[MESSAGE_TEXT]}"')
            except Exception:
                LOGGER.exception(f'\nConnection with client with username {i[DESTINATION]} lost. ')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == "__main__":
    main()
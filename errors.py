# incorrect data from socket
class IncorrectDataReceivedError(Exception):
    def __str__(self):
        return 'Incorrect message from remote client'


# server error
class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


# not dictionary args
class NonDictInputError(Exception):
    def __str__(self):
        return 'Function argument must be dictionary'


# missing required fields
class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Missing required field {self.missing_field} in the received dictionary'

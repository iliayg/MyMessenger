import random
import subprocess
import time
from itertools import cycle


# def get_name(i):
#     return f'{random.getrandbits(128)}/{i}'


PROCESSES = []
while True:
    ACTION = input('Choose an action: q - quit, '
                   's - start server and clients: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESSES.append(subprocess.Popen(f'gnome-terminal -- python3 server.py', shell=True))
        time.sleep(0.5)

        count = 0
        for el in cycle('ABC'):
            if count == 2:
                break
            PROCESSES.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n {el}', shell=True))
            count += 1
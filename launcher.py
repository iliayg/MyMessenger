import time
import subprocess
from itertools import cycle


def launch():
    names_count = 0
    PROCESSES = []
    while True:
        ACTION = input('Press "Enter" to start or "q" to quit:')
        if ACTION == 'q':
            break
        else:
            PROCESSES.append(subprocess.Popen('gnome-terminal -- python3 server.py', shell=True))
            time.sleep(0.5)
            for el in cycle('ab'):
                if names_count == 2:
                    break
                PROCESSES.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n {el}', shell=True))
                names_count += 1


if __name__ == '__main__':
    launch()
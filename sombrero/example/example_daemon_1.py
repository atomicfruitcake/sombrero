'''!
@author atomicfruitcake
@date 2018

An example python daemon
'''

from time import sleep

def example_daemon_1():
    while True:
        print('I am an example python daemon')
        sleep(10)

if __name__ == '__main__':
    example_daemon_1()

''''!
@author atomicfruitcake
@date 2018

A Daemon Manager for nohup daemons on Linux operating systems. By setting running programs with nohup, this manager will
restart programs if they crash and can be used to switch daemons on and off using a single module.
'''

import re
import shlex
import subprocess
from StringIO import StringIO
import time

import envoy

# Daemon manager scan time in seconds
daemon_master_frequency = 300

# Endpoint for output of daemon processes
nohup_endpoint = '> /dev/null 2>&1 &'

# Create a dictionary of all daemon names and associated commands here
daemon_dict = {'example_daemon_1': 'nohup python ./example/example_daemon_1.py',
               'example_daemon_2': 'nohup python ./example/example_daemon_2.py'}

daemon_names = daemon_commands = []
for daemon_name, daemon_command in daemon_dict.keys():
    daemon_names.append(daemon_name)
    daemon_commands.append(daemon_command)


def check_valid_daemon_name(daemon_name):
    '''
    Asserts that a selected daemon name is in the list of supported daemons.
    Used to check for errors before running daemon management functions
    @param daemon_name: name of the daemon to check
    '''
    assert daemon_name in daemon_names

def spawn(daemon):
    '''
    Spawns a daemon process
    @param daemon: daemon process to spawn
    '''
    print('Spawning daemon {}'.format(daemon))
    subprocess.Popen(shlex.split(daemon))

def get_daemons():
    '''
    Searches all running processes for python processes
    @return: str - all running python processes, each on an individual line
    '''
    return subprocess.check_output(('grep', 'python'), stdin=subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE).stdout)

def get_pid_from_process_string(process_string):
    return re.search(r'\d+', process_string).group()

def get_daemon_pids():
    '''
    Gets the process ids (pids) for the python daemons currently running
    @return: dict - dictionary of our python daemons pid's
    '''
    daemon_processes = get_daemons()
    daemon_pid_dict = {}
    for process_string in StringIO(daemon_processes):
        for name, command in daemon_dict.items():
            if command in process_string:
                daemon_pid_dict[name] = get_pid_from_process_string(process_string)

    return daemon_pid_dict

def stop_daemon(daemon_name):
    '''
    Stops a python daemon if it is running
    @param daemon_name: daemon to stop running
    '''
    check_valid_daemon_name(daemon_name)
    print('Stopping {} daemon'.format(daemon_name))
    status = status_daemon(daemon_name=daemon_name)
    if status is False:
        print(OSError('Unable to stop daemon, {} is already stopped'.format(daemon_name)))
        return
    target_daemon_pid = status
    print('Killing {} with pid {}'.format(daemon_name, target_daemon_pid))
    print(envoy.run('sudo kill {}'.format(target_daemon_pid)).std_out)

def status_daemon(daemon_name):
    '''
    Checks if a daemon is running. If it is running, will return pid of daemon, else will return false.
    @param daemon_name: daemon to check status
    '''
    print('Checking status of daemon {}'.format(daemon_name))
    check_valid_daemon_name(daemon_name)
    for name, pid in get_daemon_pids().items():
        if name == daemon_name:
            daemon_pid = pid
            if daemon_pid is None:
                return False
            else:
                print('{} is alive with pid {}'.format(daemon_name, daemon_pid))
                return daemon_pid

def start_daemon(daemon_name):
    '''
    Starts a python daemon if it is not running
    @param daemon_name: daemon to start running
    '''
    check_valid_daemon_name(daemon_name)
    print('Starting {} daemon'.format(daemon_name))
    if status_daemon(daemon_name=daemon_name) is True:
        raise OSError('Unable to start daemon, {} is already running'.format(daemon_name))

    for name, command in daemon_dict.items():
        if name == daemon_name:
            spawn(command + nohup_endpoint)

def restart_daemon(daemon_name):
    '''
    Stops and then starts a daemon process. This should be the main way to start a daemon
    as if the stop fails due to the daemon already being dead, this will still safely start
    a new daemon
    @param daemon_name: daemon to restart
    @return:
    '''
    print('Restarting {} daemon'.format(daemon_name))
    check_valid_daemon_name(daemon_name)
    stop_daemon(daemon_name=daemon_name)
    start_daemon(daemon_name=daemon_name)

def daemon_master(frequency):
    '''
    Runs forever checking the daemons in it's control. If it finds a dead deamon, it revives it.
    @param frequency: int - frequency
    '''
    while True:
        for daemon_name in daemon_names:
            if status_daemon(daemon_name) is False:
                print('Restarting {} daemon'.format(daemon_name))
                restart_daemon(daemon_name)
        time.sleep(frequency)

if __name__ == '__main__':
    daemon_master(daemon_master_frequency)

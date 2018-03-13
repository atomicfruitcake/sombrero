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


class DaemonManager:
    '''
    Class for managing nohup daemon processes. The class itself is run as a daemon and is responsible
    for keeping all other daemons alive
    '''
    nohup_endpoint = ' > /dev/null 2>&1 &'
    daemon_dict = {'example_daemon_1': 'nohup python ./example/example_daemon_1.py',
                   'example_daemon_2': 'nohup python ./example/example_daemon_2.py'}

    daemon_names = daemon_commands = []
    for daemon_name, daemon_command in daemon_dict.keys():
        daemon_names.append(daemon_name)
        daemon_commands.append(daemon_command)

    def __init__(self):
        self.daemon_pid_dict = self.get_daemon_pids()
        self.running_daemons = self.get_running_daemons()
        self.get_running_daemons()

    def check_valid_daemon_name(self, daemon_name):
        assert daemon_name in self.daemon_names

    def spawn(self, daemon):
        '''
        Spawns a daemon process
        @param daemon: daemon process to spawn
        '''
        print('Spawning daemon {}'.format(daemon))
        subprocess.Popen(shlex.split(daemon))

    def get_running_daemons(self):
        '''
        Searches all running processes for python processes
        @return: str - all running python processes, each on an individual line
        '''
        return subprocess.check_output(('grep', 'python'), stdin=subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE).stdout)

    def get_pid_from_process_string(self, process_string):
        return re.search(r'\d+', process_string).group()

    def get_daemon_pids(self):
        '''
        Gets the process ids (pids) for the python daemons currently running
        @return: dict - dictionary of our python daemons pid's
        '''
        print('Getting daemon process ids')
        daemon_processes = self.get_running_daemons()
        daemon_pid_dict = {}
        for process_string in StringIO.StringIO(daemon_processes):
            for name, command in self.daemon_dict.items():
                if command in process_string:
                    daemon_pid_dict[name] = self.get_pid_from_process_string(process_string)

        return daemon_pid_dict

    def stop_daemon(self, daemon_name):
        '''
        Stops a python daemon if it is running
        @param daemon_name: daemon to stop running
        '''
        self.check_valid_daemon_name(daemon_name)
        print('Stopping {} daemon'.format(daemon_name))
        status = self.status_daemon(daemon_name=daemon_name)
        if status is False:
            print('Unable to stop daemon, {} is already stopped'.format(daemon_name))
        target_daemon_pid = status
        print('Killing {} with pid {}'.format(daemon_name, target_daemon_pid))
        r = envoy.run('sudo kill {}'.format(target_daemon_pid))
        print(r.std_out)

    def status_daemon(self, daemon_name):
        '''
        Checks if a daemon is running. If it is running, will return pid of daemon, else will return false.
        @param daemon_name: daemon to check status
        @return status: pid of daemon, otherwise will return False
        '''
        print('Checking status of daemon {}'.format(daemon_name))
        self.check_valid_daemon_name(daemon_name)
        for name, pid in self.daemon_pid_dict.items():
            if name == daemon_name:
                daemon_pid = pid
                if daemon_pid is None:
                    return False
                else:
                    print('{} is alive with pid {}'.format(daemon_name, daemon_pid))
                    return daemon_pid
            else:
                continue
        return False

    def start_daemon(self, daemon_name):
        '''
        Starts a python daemon if it is not running
        @param daemon_name: daemon to start running
        '''
        self.check_valid_daemon_name(daemon_name)
        print('Starting {} daemon'.format(daemon_name))
        if self.status_daemon(daemon_name=daemon_name) is True:
            raise OSError('Unable to start daemon, {} is already running'.format(daemon_name))
        for i in range(len(self.daemon_names)):
            if daemon_name == self.daemon_names[i]:
                self.spawn(self.daemons[i] + self.nohup_endpoint)

    def restart_daemon(self, daemon_name):
        '''
        Stops and then starts a daemon process. This should be the main way to start a daemon
        as if the stop fails due to the daemon already being dead, this will still safely start
        a new daemon
        @param daemon_name: daemon to restart
        '''
        print('Restarting {} daemon'.format(daemon_name))
        self.check_valid_daemon_name(daemon_name)
        self.stop_daemon(daemon_name=daemon_name)
        self.start_daemon(daemon_name=daemon_name)

def daemon_master(frequency=300):
    '''
    Runs forever checking the daemons in it's control. If it finds a dead deamon, it revives it.
    @param frequency: int - frequency
    '''

    while True:
        dm = DaemonManager()
        dm.get_daemon_pids()
        for daemon_name in dm.daemon_names:
            if dm.status_daemon(daemon_name) is False:
                dm.restart_daemon(daemon_name)
        del dm
        print('Waiting for {} seconds'.format(str(frequency)))
        time.sleep(frequency)


if __name__ == '__main__':
    daemon_master()

'''!
@author atomicfruitcake
@date 2018

Tests for the daemon manager
'''
import unittest
from sombrero import sombrero

class TestDaemonManager(unittest.TestCase):
    def test_get_daemons(self):
        self.assertEquals(type(sombrero.get_daemons()), str)

    def test_get_daemon_pids(self):
        self.assertEquals(type(sombrero.get_daemon_pids()), dict)

    def test_status_daemon(self):
        self.assertEquals(type(sombrero.status_daemon('smc')), bool)


if __name__ == '__main__':
    unittest.main()

import unittest
import logging
import sys
import time

from TorrentPython.PeerService import *
from TorrentPython.TorrentUtils import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'

TRANSMISSION_IP = '192.168.10.5'
TRANSMISSION_PORT = 51413


class PeerServiceTest(unittest.TestCase):

    def setUp(self):
        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT
        self.info_hash = INFO_HASH
        self.peer_id = TorrentUtils.getPeerID()
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_handShake(self):
        testObj = PeerService(self.info_hash, self.peer_id)
        self.assertIsNotNone(testObj)
        self.assertTrue(testObj.handShake(self.peer_ip, self.peer_port))

        time.sleep(2000)
        del testObj


if __name__ == '__main__':
    unittest.main()

import unittest
import logging
import sys
import time

from TorrentPython.PeerService import *
from TorrentPython.TorrentUtils import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.10.5'
TRANSMISSION_PORT = 51413


class PeerServiceTest(unittest.TestCase):

    def setUp(self):
        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT
        self.metainfo = MetaInfo.createFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(self.metainfo)
        self.peer_id = TorrentUtils.getPeerID()
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_handShake(self):
        testObj = PeerService(self.metainfo, self.peer_id)
        self.assertIsNotNone(testObj)
        self.assertTrue(testObj.handShake(self.peer_ip, self.peer_port))

        time.sleep(2000)
        del testObj


if __name__ == '__main__':
    unittest.main()

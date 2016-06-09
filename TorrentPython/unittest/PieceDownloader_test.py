import unittest
import time

from TorrentPython.PieceDownloader import *
from TorrentPython.TorrentUtils import *

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.10.5'
TRANSMISSION_PORT = 51413


class PieceDownloaderTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.createFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(self.metainfo)
        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_create(self):
        testObj = PieceDownloader.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port, [0])
        self.assertIsNotNone(testObj)
        testObj.subscribe(lambda x: print(len(x[1])))

        time.sleep(100000)
        del testObj

if __name__ == '__main__':
    unittest.main()

import unittest
import time

from TorrentPython.PeerRadio import *
from TorrentPython.TorrentUtils import *

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.10.11'
TRANSMISSION_PORT = 51413


class PeerRadioTest(unittest.TestCase):

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
        testObj = PeerRadio.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        def handler(msg: Message):
            if msg.id == Message.PIECE:
                print(msg.index, msg.begin)

        testObj.subscribe(on_next=handler, on_completed=lambda: print("completed!"))

        time.sleep(5)

        for i in range(0, 300):
            for j in range(0, 32):
                testObj.request(i, PeerRadio.BLOCK_SIZE * j)

            if i % 8 == 0:
                time.sleep(1)

        time.sleep(100000)
        del testObj

if __name__ == '__main__':
    unittest.main()

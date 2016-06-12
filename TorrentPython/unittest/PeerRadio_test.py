import unittest
import time
from threading import *

from TorrentPython.PeerRadio import *
from TorrentPython.TorrentUtils import *

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.0.6'
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
    def test_disconnected(self):

        endEvent = Event()

        testObj = PeerRadio.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        def on_next(msg: Message):
            print(msg)

            if msg.id == Message.UNCHOCK:
                testObj.request(0, 0)

        def on_completed():
            print("completed!")
            endEvent.set()

        testObj.subscribe(on_next=on_next, on_completed=on_completed)
        endEvent.wait()

        del testObj

    @unittest.skip("clear")
    def test_(self):
        testObj = PeerRadio.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        def handler(msg: Message):
            if msg.id == Message.PIECE:
                print(msg.index, msg.begin)

        testObj.subscribe(on_next=handler, on_completed=lambda: print("completed!"))

        # time.sleep(10)
        #
        # for i in range(0, 1310):
        #     for j in range(0, 32):
        #         testObj.request(i, PeerRadio.BLOCK_SIZE * j)
        #
        #     if i % 8 == 0:
        #         time.sleep(1)

        time.sleep(100000)
        del testObj

if __name__ == '__main__':
    unittest.main()

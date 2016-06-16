import unittest
import time
from threading import Event

from TorrentPython.PieceHunter import *
from TorrentPython.TorrentUtils import *

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.10.11'
TRANSMISSION_PORT = 51413

SAMPLE_BUF_64_BYTES_OF_PIECE_0 = b'ER\x08\x00\x00\x00\x90\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\xed\xfa\x8e\xd5\xbc\x00|\xfb\xfcf1\xdbf1\xc9fSfQ\x06W\x8e\xdd\x8e\xc5R\xbe\x00|\xbf\x00'


class PeerRadioTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(TORRENT_PATH)
        self.assertIsNotNone(self.metainfo)
        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_create(self):
        testObj = PieceHunter(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)
        testObj.subscribe(lambda x: print(x.id))
        testObj.destroy()
        del testObj

    @unittest.skip("clear")
    def test_connect_disconnect(self):
        testObj = PieceHunter(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)
        testObj.subscribe(lambda x: print(x.id))
        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))
        time.sleep(5)
        testObj.destroy()
        del testObj

    @unittest.skip("clear")
    def test_hunt(self):
        endEvent = Event()

        testObj = PieceHunter(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)

        class PieceHunterObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id)

                if msg.id == PieceHunterMessage.PIECE:
                    print(msg.payload[0])

                if msg.id == PieceHunterMessage.COMPLETED:
                    self.endEvent.set()

                if msg.id == PieceHunterMessage.INTERRUPTED:
                    self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        testObj.subscribe(PieceHunterObserver(endEvent))
        testObj.connect(self.peer_ip, self.peer_port)

        piece_indices = [i for i in range(0, self.metainfo.get_info().getPieceNum())]
        testObj.hunt(piece_indices, 10, 5)

        endEvent.wait()

        testObj.destroy()
        del testObj

    # @unittest.skip("clear")
    def test_hunt_timeout(self):
        endEvent = Event()

        testObj = PieceHunter(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)

        class PieceHunterObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id)

                if msg.id == PieceHunterMessage.PIECE:
                    print(msg.payload[0])

                if msg.id == PieceHunterMessage.COMPLETED:
                    self.endEvent.set()

                if msg.id == PieceHunterMessage.INTERRUPTED:
                    self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        testObj.subscribe(PieceHunterObserver(endEvent))
        testObj.connect(self.peer_ip, self.peer_port)

        piece_indices = [1404]
        testObj.hunt(piece_indices, 10, 5)

        endEvent.wait()

        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

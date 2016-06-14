import unittest

from TorrentPython.PieceHunter import *
from TorrentPython.TorrentUtils import *

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.10.11'
TRANSMISSION_PORT = 51413

SAMPLE_BUF_64_BYTES_OF_PIECE_0 = b'ER\x08\x00\x00\x00\x90\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003\xed\xfa\x8e\xd5\xbc\x00|\xfb\xfcf1\xdbf1\xc9fSfQ\x06W\x8e\xdd\x8e\xc5R\xbe\x00|\xbf\x00'


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

    @unittest.skip("clear")
    def test_create(self):
        testObj = PieceHunter.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)
        del testObj

    @unittest.skip("clear")
    def test_hunt(self):
        endEvent = Event()

        testObj = PieceHunter.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        class PrizeObserver(Observer):
            def on_next(self, msg):
                self.assertEqual(SAMPLE_BUF_64_BYTES_OF_PIECE_0, msg[1][:64])

            def on_completed(self):
                print('on_completed')
                endEvent.set()

            def on_error(self, e):
                print(e)
                endEvent.set()

        prize = testObj.hunt(PrizeObserver, [0], 10, 5)
        self.assertIsNotNone(prize)

        endEvent.wait()
        del testObj

    # @unittest.skip("clear")
    def test_hunt_beta(self):
        endEvent = Event()

        testObj = PieceHunter.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        class PrizeObserver(Observer):
            def __init__(self, event):
                self.endEvent = event
                self.fp = open('D:/ubuntu.iso', 'wb')

            def on_next(self, msg):
                print(msg[0])
                self.fp .write(msg[1])

            def on_completed(self):
                print('on_completed')
                self.fp.close()
                self.endEvent.set()

            def on_error(self, e):
                print(e)
                self.fp.close()
                self.endEvent.set()

        piece_indices = [i for i in range(0, self.metainfo.getInfo().getPieceNum())]
        prize = testObj.hunt(PrizeObserver(endEvent), piece_indices, 10, 5)
        self.assertIsNotNone(prize)

        endEvent.wait()

        print(testObj.average_performance)
        del testObj

    @unittest.skip("clear")
    def test_on_error_delay_timeout(self):
        endEvent = Event()

        testObj = PieceHunter.create(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        class PrizeObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg[0])

            def on_completed(self):
                print('on_completed')
                endEvent.set()

            def on_error(self, e):
                print(e)
                endEvent.set()

        prize = testObj.hunt(PrizeObserver(endEvent), [1300], 10, 10)
        self.assertIsNotNone(prize)

        endEvent.wait()
        del testObj

if __name__ == '__main__':
    unittest.main()

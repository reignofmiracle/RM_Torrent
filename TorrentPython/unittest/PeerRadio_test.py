import unittest
from threading import Event

from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.PeerRadio import PeerRadio, Observer
from TorrentPython.TorrentUtils import TorrentUtils

import time

TORRENT_PATH = '../Resources/sample.torrent'

TRANSMISSION_IP = '192.168.0.11'
TRANSMISSION_PORT = 51413


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
    def test_new(self):
        testObj = PeerRadio(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        time.sleep(10)
        testObj.subscribe(on_completed=lambda: print('on_completed'))
        del testObj

    @unittest.skip("wait")
    def test_request(self):
        testObj = PeerRadio(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)
        self.assertTrue(testObj.request(0, 0, 0))
        del testObj

    # @unittest.skip("wait")
    def test_get_bitfield(self):
        endEvent = Event()

        testObj = PeerRadio(self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)

        class PeerRadioObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg)
                endEvent.set()

            def on_completed(self):
                print('on_completed')
                endEvent.set()

            def on_error(self, e):
                print(e)
                endEvent.set()

        testObj.subscribe(PeerRadioObserver(endEvent))
        endEvent.wait()

        testObj.clear()
        del testObj

if __name__ == '__main__':
    unittest.main()

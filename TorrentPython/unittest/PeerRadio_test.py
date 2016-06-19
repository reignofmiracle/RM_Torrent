import unittest
import time
from threading import Event

from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.PeerMessage import Message
from TorrentPython.PeerRadio import PeerRadio, Observer, PeerRadioMessage
from TorrentPython.TorrentUtils import TorrentUtils

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROOT_TORRENT_PATH = '../Resources/root.torrent'

TRANSMISSION_IP = '192.168.0.6'
TRANSMISSION_PORT = 51413


class PeerRadioTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        # self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        self.assertIsNotNone(self.metainfo)
        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_new(self):
        testObj = PeerRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)
        testObj.subscribe(on_completed=lambda: print('on_completed'))
        testObj.destroy()
        del testObj

    @unittest.skip("clear")
    def test_connect_destroy(self):
        testObj = PeerRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)
        testObj.subscribe(lambda x: print(x.id))
        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))
        time.sleep(4)
        testObj.destroy()
        del testObj

    @unittest.skip("clear")
    def test_reconnect(self):
        testObj = PeerRadio(self.client_id, self.metainfo)
        testObj.subscribe(lambda x: print(x.id))
        self.assertIsNotNone(testObj)
        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))
        self.assertFalse(testObj.connect(self.peer_ip, self.peer_port))
        testObj.destroy()
        del testObj

    @unittest.skip("wait")
    def test_connect_disconnect(self):
        testObj = PeerRadio(self.client_id, self.metainfo)
        testObj.subscribe(lambda x: print(x.id))
        self.assertIsNotNone(testObj)
        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))
        time.sleep(10)
        testObj.disconnect()

        time.sleep(1)

        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))
        time.sleep(10)
        testObj.disconnect()
        testObj.destroy()
        del testObj

    # @unittest.skip("clear")
    def test_request(self):
        endEvent = Event()

        testObj = PeerRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)

        class PeerRadioObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id)
                if msg.id == PeerRadioMessage.RECEIVED:
                    payload = msg.payload
                    if payload.id == Message.UNCHOCK:
                        print(testObj.request(0, 0, 1024))

                    if payload.id == Message.PIECE:
                        self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        testObj.subscribe(PeerRadioObserver(endEvent))
        testObj.connect(self.peer_ip, self.peer_port)

        endEvent.wait()

        testObj.destroy()
        del testObj

    @unittest.skip("clear")
    def test_completed_when_error(self):
        endEvent = Event()

        testObj = PeerRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)

        class PeerRadioObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id, msg.payload)
                if msg.id == PeerRadioMessage.DISCONNECTED:
                    self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        testObj.subscribe(PeerRadioObserver(endEvent))
        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))

        endEvent.wait()

        testObj.destroy()
        del testObj

if __name__ == '__main__':

    unittest.main()

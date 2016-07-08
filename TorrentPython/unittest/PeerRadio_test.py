import unittest
import time
from threading import Event

from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.PeerMessage import Message
from TorrentPython.PeerRadio import PeerRadio
from TorrentPython.TorrentUtils import TorrentUtils

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROOT_TORRENT_PATH = '../Resources/root.torrent'

PEER_IP = '192.168.10.12'
PEER_PORT = 51413

# PEER_IP = '5.79.161.247'
# PEER_PORT = 6881


class PeerRadioTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        # self.metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        self.assertIsNotNone(self.metainfo)
        self.peer_ip = PEER_IP
        self.peer_port = PEER_PORT
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_start(self):
        test_obj = PeerRadio.start(self.client_id, self.metainfo)
        self.assertIsNotNone(test_obj)
        test_obj.stop()

    @unittest.skip("clear")
    def test_connect(self):
        test_obj = PeerRadio.start(self.client_id, self.metainfo)
        self.assertIsNotNone(test_obj)

        test_obj.subscribe(lambda msg: print(msg.get('id'), msg.get('payload')))
        test_obj.connect(self.peer_ip, self.peer_port)

        time.sleep(300)

        test_obj.stop()

    # @unittest.skip("clear")
    def test_disconnect(self):
        test_obj = PeerRadio.start(self.client_id, self.metainfo)
        self.assertIsNotNone(test_obj)

        end_event = Event()

        test_obj.subscribe(lambda msg: print(msg.get('id'), msg.get('payload')))
        test_obj.subscribe(
            lambda msg: test_obj.stop() if msg.get('id') == 'msg' and msg.get('payload').id == Message.UNCHOCK else None)
        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'disconnected' else None)
        test_obj.subscribe(on_completed=lambda: end_event.set())
        test_obj.subscribe(on_completed=lambda: print('on_completed'))

        test_obj.connect(self.peer_ip, self.peer_port)

        end_event.wait()
        test_obj.stop()

    @unittest.skip("clear")
    def test_connect2(self):
        test_obj = PeerRadio.start(self.client_id, self.metainfo)
        self.assertIsNotNone(test_obj)

        end_event = Event()

        test_obj.subscribe(lambda msg: print(msg.get('id'), msg.get('payload')))
        # test_obj.subscribe(
        #     lambda msg: test_obj.stop() if msg.get('id') == 'msg' and msg.get('payload').id == Message.UNCHOCK else None)
        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'disconnected' else None)
        test_obj.subscribe(on_completed=lambda: end_event.set())
        test_obj.subscribe(on_completed=lambda: print('on_completed'))

        test_obj.connect(self.peer_ip, self.peer_port)

        end_event.wait()
        test_obj.stop()

    @unittest.skip("clear")
    def test_request(self):
        test_obj = PeerRadio.start(self.client_id, self.metainfo)
        self.assertIsNotNone(test_obj)

        end_event = Event()

        test_obj.subscribe(lambda msg: print(msg.get('id'), msg.get('payload')))

        def handler(msg):
            if msg.get('id') == 'msg':
                payload = msg.get('payload')

                if payload.id == Message.UNCHOCK:
                    test_obj.request(0, 0, 2 ** 14)

                if payload.id == Message.PIECE:
                    end_event.set()

        test_obj.subscribe(lambda msg: handler(msg))
        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'disconnected' else None)
        test_obj.subscribe(on_completed=lambda: end_event.set())
        test_obj.subscribe(on_completed=lambda: print('on_completed'))

        test_obj.connect(self.peer_ip, self.peer_port)

        end_event.wait()
        test_obj.stop()

if __name__ == '__main__':
    unittest.main()

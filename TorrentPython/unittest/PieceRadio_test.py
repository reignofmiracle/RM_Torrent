import shutil
import filecmp
import random

import unittest
import time
from threading import Event

from TorrentPython.PieceAssembler import *
from TorrentPython.PieceRadio import *
from TorrentPython.TorrentUtils import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROOT_TORRENT_PATH = '../Resources/root.torrent'

PEER_IP = '192.168.10.12'
# PEER_IP = '192.168.0.5'
PEER_PORT = 51413


class PieceRadioTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.peer_ip = PEER_IP
        self.peer_port = PEER_PORT
        self.dest_question = 'D:/sandbox/'
        self.dest_answer = 'D:/sandbox2/'
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_start(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceRadio.start(self.client_id, metainfo)
        self.assertIsNotNone(testObj)
        testObj.stop()

    # @unittest.skip("clear")
    def test_request_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(metainfo)

        test_obj = PieceRadio.start(self.client_id, metainfo)
        self.assertIsNotNone(test_obj)

        end_event = Event()

        received_piece = []

        # def check_bitfield(msg):
        #     if msg.get('id') == 'bitfield':
        #         payload = msg.get('payload')
        #         completed_piece_indices = payload.get_completed_piece_indices()
        #         print(completed_piece_indices)
        #         end_event.set()
        #
        # test_obj.subscribe(check_bitfield)

        test_obj.subscribe(
            lambda msg: print('piece', msg.get('payload')[0]) if msg.get('id') == 'piece' else None)

        test_obj.subscribe(
            lambda msg: received_piece.append(msg.get('payload')[0]) if msg.get('id') == 'piece' else None)

        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'completed' else None)

        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'interrupted' else None)

        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'disconnected' else None)

        self.assertTrue(test_obj.connect(self.peer_ip, self.peer_port))

        # piece_indices = [i for i in range(0, metainfo.get_info().get_piece_num())]
        piece_indices = [0, 1, 2, 3, 4]
        # random.shuffle(piece_indices)
        test_obj.request(piece_indices)

        end_event.wait()
        test_obj.stop()

        self.assertEqual(piece_indices, received_piece)

if __name__ == '__main__':
    unittest.main()

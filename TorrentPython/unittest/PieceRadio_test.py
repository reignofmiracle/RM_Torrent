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

    # @unittest.skip("clear")
    def test_start(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceRadio.start(self.client_id, metainfo)
        self.assertIsNotNone(testObj)
        testObj.stop()

    # @unittest.skip("clear")
    def test_request_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(metainfo)

        info = metainfo.get_info()
        if os.path.exists(self.dest_question + info.get_name().decode()):
            os.remove(self.dest_question + info.get_name().decode())

        piece_assembler = PieceAssembler.start(metainfo, self.dest_question)

        test_obj = PieceRadio.start(self.client_id, metainfo)
        self.assertIsNotNone(test_obj)

        end_event = Event()

        received_piece_indices = []

        def write_piece(msg):
            if msg.get('id') == 'piece':
                print(msg.get('payload')[0])
                received_piece_indices.append(msg.get('payload')[0])
                piece_assembler.write(*msg.get('payload'))

        test_obj.subscribe(lambda msg: write_piece(msg))

        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'completed' else None)

        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'interrupted' else None)

        test_obj.subscribe(
            lambda msg: end_event.set() if msg.get('id') == 'disconnected' else None)

        test_obj.connect(self.peer_ip, self.peer_port)
        test_obj.set_piece_per_step(10)
        test_obj.set_peer_radio_timeout(5)

        piece_indices = [i for i in range(0, metainfo.get_info().get_piece_num())]
        random.shuffle(piece_indices)
        test_obj.request(piece_indices)

        end_event.wait()
        test_obj.stop()
        piece_assembler.stop()

        self.assertEqual(piece_indices, received_piece_indices)

        self.assertTrue(
            filecmp.cmp(self.dest_question + info.get_name().decode(),
                        self.dest_answer + info.get_name().decode()))

if __name__ == '__main__':
    unittest.main()

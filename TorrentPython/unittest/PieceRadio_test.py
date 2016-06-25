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

TRANSMISSION_IP = '192.168.0.9'
TRANSMISSION_PORT = 51413


class PieceRadioTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT
        self.dest_question = 'D:/sandbox/'
        self.dest_answer = 'D:/sandbox2/'
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_create(self):
        testObj = PieceRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)
        testObj.subscribe(lambda x: print(x.id))
        testObj.destroy()
        del testObj

    @unittest.skip("clear")
    def test_connect_disconnect(self):
        testObj = PieceRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)
        testObj.subscribe(lambda x: print(x.id))
        self.assertTrue(testObj.connect(self.peer_ip, self.peer_port))
        time.sleep(5)
        testObj.destroy()
        del testObj

    # @unittest.skip("clear")
    def test_request_M(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        self.assertIsNotNone(metainfo)

        info = metainfo.get_info()
        if os.path.isdir(self.dest_question + info.get_name().decode()):
            shutil.rmtree(self.dest_question + info.get_name().decode())

        piece_assembler = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(piece_assembler.prepare())

        endEvent = Event()

        piece_radio = PieceRadio(self.client_id, metainfo)
        self.assertIsNotNone(piece_radio)

        received_piece_indices = []

        class PieceRadioObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id)

                if msg.id == PieceRadioMessage.PIECE:
                    print(msg.payload[0])
                    received_piece_indices.append(msg.payload[0])
                    piece_assembler.write(*msg.payload)

                if msg.id == PieceRadioMessage.COMPLETED:
                    self.endEvent.set()

                if msg.id == PieceRadioMessage.INTERRUPTED:
                    self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        piece_radio.subscribe(PieceRadioObserver(endEvent))
        piece_radio.connect(self.peer_ip, self.peer_port)

        piece_indices = [i for i in range(0, metainfo.get_info().get_piece_num())]
        random.shuffle(piece_indices)
        piece_radio.request(piece_indices, 100, 5)

        endEvent.wait()

        self.assertEqual(piece_indices, received_piece_indices)

        for file in info.iter_files():
            self.assertTrue(
                filecmp.cmp(self.dest_question + file.get_full_path().decode(),
                            self.dest_answer + file.get_full_path().decode()))

        piece_radio.destroy()
        del piece_radio

        piece_assembler.destroy()
        del piece_assembler

    @unittest.skip("clear")
    def test_request_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(metainfo)

        info = metainfo.get_info()
        if os.path.exists(self.dest_question + info.get_name().decode()):
            os.remove(self.dest_question + info.get_name().decode())

        piece_assembler = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(piece_assembler.prepare())

        endEvent = Event()

        piece_radio = PieceRadio(self.client_id, metainfo)
        self.assertIsNotNone(piece_radio)

        received_piece_indices = []

        class PieceRadioObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id)

                if msg.id == PieceRadioMessage.PIECE:
                    print(msg.payload[0])
                    received_piece_indices.append(msg.payload[0])
                    piece_assembler.write(*msg.payload)

                if msg.id == PieceRadioMessage.COMPLETED:
                    self.endEvent.set()

                if msg.id == PieceRadioMessage.INTERRUPTED:
                    self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        piece_radio.subscribe(PieceRadioObserver(endEvent))
        piece_radio.connect(self.peer_ip, self.peer_port)

        piece_indices = [i for i in range(0, metainfo.get_info().get_piece_num())]
        random.shuffle(piece_indices)
        piece_radio.request(piece_indices, 10, 5)

        endEvent.wait()

        self.assertEqual(piece_indices, received_piece_indices)

        self.assertTrue(
            filecmp.cmp(self.dest_question + info.get_name().decode(),
                        self.dest_answer + info.get_name().decode()))

        piece_radio.destroy()
        del piece_radio

        piece_assembler.destroy()
        del piece_assembler

    @unittest.skip("clear")
    def test_request_timeout(self):
        endEvent = Event()

        testObj = PieceRadio(self.client_id, self.metainfo)
        self.assertIsNotNone(testObj)

        class PieceRadioObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg.id)

                if msg.id == PieceRadioMessage.PIECE:
                    print(msg.payload[0])

                if msg.id == PieceRadioMessage.COMPLETED:
                    self.endEvent.set()

                if msg.id == PieceRadioMessage.INTERRUPTED:
                    self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                pass

        testObj.subscribe(PieceRadioObserver(endEvent))
        testObj.connect(self.peer_ip, self.peer_port)

        piece_indices = [1404]
        testObj.request(piece_indices, 10, 5)

        endEvent.wait()

        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

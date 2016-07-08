import unittest
from threading import Event
import filecmp

from TorrentPython.HuntingScheduler import HuntingScheduler

from TorrentPython.MetaInfo import *
from TorrentPython.PieceHunter import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

from TorrentPython.PieceAssembler import *
from TorrentPython.PeerProvider import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'

PEER_IP = '5.79.161.247'
PEER_PORT = 6881


class PieceHunterTest(unittest.TestCase):
    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.dest_question = 'D:/sandbox/'
        self.dest_answer = 'D:/sandbox2/'
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)

        self.piece_assembler = PieceAssembler(self.metainfo, self.dest_question)
        self.hunting_scheduler = HuntingScheduler(self.piece_assembler)

        self.peer_ip = PEER_IP
        self.peer_port = PEER_PORT

    def tearDown(self):
        self.hunting_scheduler.stop()
        self.piece_assembler.stop()

    @unittest.skip("clear")
    def test_create(self):
        testObj = PieceHunter.start(
            self.hunting_scheduler, self.piece_assembler, self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)
        testObj.stop()

    # @unittest.skip("clear")
    def test_download(self):
        test_obj = PieceHunter.start(
            self.hunting_scheduler, self.piece_assembler, self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(test_obj)

        endEvent = Event()
        test_obj.subscribe(on_next=lambda x: print(x), on_completed=lambda: endEvent.set())
        test_obj.connect()

        endEvent.wait()
        test_obj.stop()

if __name__ == '__main__':
    unittest.main()

import unittest
from TorrentPython.HuntingScheduler import HuntingScheduler

from TorrentPython.MetaInfo import *
from TorrentPython.PieceHunter import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

from TorrentPython.PieceAssembler import *
from TorrentPython.PeerDetective import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'

TRANSMISSION_IP = '192.168.0.5'
TRANSMISSION_PORT = 51413


class PieceHunterTest(unittest.TestCase):
    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.path = 'D:/sandbox/'
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)

        self.piece_assembler = PieceAssembler(self.metainfo, self.path)
        self.hunting_scheduler = HuntingScheduler(self.piece_assembler)

        self.peer_ip = TRANSMISSION_IP
        self.peer_port = TRANSMISSION_PORT

    def tearDown(self):
        self.hunting_scheduler.destroy()
        self.piece_assembler.destroy()

    # @unittest.skip("clear")
    def test_create(self):
        testObj = PieceHunter(
            self.hunting_scheduler, self.piece_assembler, self.client_id, self.metainfo, self.peer_ip, self.peer_port)
        self.assertIsNotNone(testObj)
        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

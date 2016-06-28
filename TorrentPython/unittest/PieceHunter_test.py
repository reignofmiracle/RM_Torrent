import unittest

from TorrentPython.MetaInfo import *
from TorrentPython.PieceHunter import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

from TorrentPython.PieceAssembler import *
from TorrentPython.PeerDetective import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class PieceHunterTest(unittest.TestCase):
    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.path = 'D:/sandbox/'
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)

        # self.piece_assembler = PieceAssembler(self.metainfo, self.path)
        # self.hunting_scheduler = HuntingScheduler(self.piece_assembler)

    def tearDown(self):
        self.piece_assembler.destroy()

    @unittest.skip("clear")
    def test_create(self):
        testObj = PieceHunter()

if __name__ == '__main__':
    unittest.main()

import unittest

from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.PieceHunterManager import PieceHunterManager
from TorrentPython.RoutingTable import RoutingTable
from TorrentPython.TorrentUtils import TorrentUtils

from TorrentPython.PieceAssembler import *
from TorrentPython.PeerDetective import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class MetaInfoTest(unittest.TestCase):
    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.path = 'D:/sandbox/'
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)

        self.piece_assembler = PieceAssembler(self.metainfo, self.path)
        self.peer_detective = PeerDetective(self.client_id, self.routing_table)

    def tearDown(self):
        self.piece_assembler.destroy()
        self.peer_detective.destroy()

    @unittest.skip("clear")
    def test_new(self):
        testObj = PieceHunterManager(self.piece_assembler, self.peer_detective)
        self.assertIsNotNone(testObj)
        testObj.destroy()
        del testObj

    # @unittest.skip("wait")
    def test_expand(self):
        testObj = PieceHunterManager(self.piece_assembler, self.peer_detective)
        self.assertIsNotNone(testObj)
        new_hunters = testObj.expand()
        print(new_hunters)
        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

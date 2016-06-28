import unittest

from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.PieceAssembler import PieceAssembler
from TorrentPython.HuntingScheduler import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'


class PieceHunterTest(unittest.TestCase):
    def setUp(self):
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.path = 'D:/sandbox/'

        self.piece_assembler = PieceAssembler(self.metainfo, self.path)

    def tearDown(self):
        self.piece_assembler.destroy()

    @unittest.skip("clear")
    def test_new(self):
        testObj = HuntingScheduler(self.piece_assembler)
        self.assertIsNotNone(testObj)
        testObj.destroy()
        del testObj

    # @unittest.skip("clear")
    def test_get_order(self):
        testObj = HuntingScheduler(self.piece_assembler)
        self.assertIsNotNone(testObj)

        orders = []
        for i in range(1310):
            orders.append(testObj.get_order())

        orders.sort()
        self.assertEqual([i for i in range(1310)], orders)

        order = testObj.get_order()
        self.assertIsNone(order)

        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

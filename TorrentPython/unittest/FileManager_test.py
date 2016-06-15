import unittest

from TorrentPython.FileManager import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROOT_TORRENT_PATH = '../Resources/root.torrent'


class FileManagerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_prepare_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertTrue(testObj.prepare())
        pass

    @unittest.skip("clear")
    def test_prepare_M(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertTrue(testObj.prepare())
        pass

    @unittest.skip("wait")
    def test_getMissingPieceIndices_S_F(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertEqual([i for i in range(0, 384)], testObj.getMissingPieceIndices())
        pass

    @unittest.skip("wait")
    def test_getMissingPieceIndices_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertEqual([], testObj.getMissingPieceIndices())
        pass

    # @unittest.skip("clear")
    def test_getMissingPieceIndices_M_F(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertEqual([i for i in range(0, 384)], testObj.getMissingPieceIndices())
        pass

    # @unittest.skip("clear")
    def test_getMissingPieceIndices_M_S(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertEqual([], testObj.getMissingPieceIndices())
        pass

if __name__ == '__main__':
    unittest.main()

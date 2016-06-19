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
    def test_get_missing_piece_indices_S_F(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertEqual([i for i in range(0, 384)], testObj.get_missing_piece_Indices())
        pass

    @unittest.skip("wait")
    def test_get_missing_piece_indices_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertEqual([], testObj.get_missing_piece_Indices())
        pass

    # @unittest.skip("clear")
    def test_get_missing_piece_indices_M_F(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertTrue(testObj.prepare())

        info = metainfo.get_info()
        self.assertEqual([i for i in range(0, info.get_piece_num())], testObj.get_missing_piece_Indices())
        pass

    # @unittest.skip("clear")
    def test_get_missing_piece_indices_M_S(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox2/')
        self.assertTrue(testObj.prepare())

        self.assertEqual([], testObj.get_missing_piece_Indices())
        pass

    # @unittest.skip("clear")
    def test_get_missing_piece_indices_S_F(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox/')
        self.assertTrue(testObj.prepare())

        info = metainfo.get_info()
        self.assertEqual([i for i in range(0, info.get_piece_num())], testObj.get_missing_piece_Indices())
        pass

    # @unittest.skip("clear")
    def test_get_missing_piece_indices_S_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = FileManager(metainfo, 'D:/sandbox2/')
        self.assertTrue(testObj.prepare())
        self.assertEqual([], testObj.get_missing_piece_Indices())
        pass

if __name__ == '__main__':
    unittest.main()

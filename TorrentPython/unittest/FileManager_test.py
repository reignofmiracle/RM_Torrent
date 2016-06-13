import unittest

from TorrentPython.FileManager import *

TORRENT_PATH = '../Resources/root.torrent'


class FileManagerTest(unittest.TestCase):
    def setUp(self):
        self.metainfo = MetaInfo.createFromTorrent(TORRENT_PATH)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_buildCastle(self):
        testObj = FileManager(self.metainfo, 'D:/sandbox/')
        self.assertTrue(testObj.buildCastle())
        pass

if __name__ == '__main__':
    unittest.main()

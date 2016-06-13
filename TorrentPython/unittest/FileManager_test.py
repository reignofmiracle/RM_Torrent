import unittest

from TorrentPython.FileManager import *

TORRENT_PATH = '../Resources/sample.torrent'


class FileManagerTest(unittest.TestCase):
    def setUp(self):
        self.metainfo = MetaInfo.createFromTorrent(TORRENT_PATH)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_buildCastle(self):
        testObj = FileManager(self.metainfo, 'D:/sandbox/castle/')
        self.assertTrue(testObj.buildCastle(clear=True))
        pass

if __name__ == '__main__':
    unittest.main()

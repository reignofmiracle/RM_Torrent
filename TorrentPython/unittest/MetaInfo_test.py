import unittest

from TorrentPython.MetaInfo import *

MAGNET_STR = 'magnet:?xt=urn:btih:699CDA895AF6FBD5A817FFF4FE6FA8AB87E36F48'
TORRENT_PATH = '../Resources/sample.torrent'


class MetaInfoTest(unittest.TestCase):
    def setUp(self):                              
        pass

    def tearDown(self):
        pass

    @unittest.skip("wait")
    def test_parseMagnet(self):
        metaInfo = MetaInfo.parseMagnet(MAGNET_STR)
        self.assertIsNotNone(metaInfo)
        
    @unittest.skip("clear")
    def test_parseTorrent(self):
        metaInfo = MetaInfo.parseTorrent(TORRENT_PATH)
        self.assertIsNotNone(metaInfo)
        self.assertTrue(metaInfo[b'announce'] == b'udp://tracker.openbittorrent.com:80/announce')

    @unittest.skip("clear")
    def test_getInfoHashFromTorrent(self):
        info_hash = MetaInfo.getInfoHashFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(info_hash)
        print(info_hash)

    # @unittest.skip("clear")
    def test_createFromTorrent(self):
        metainfo = MetaInfo.createFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(metainfo)
        self.assertEqual(524288, metainfo.getPieceLength())


if __name__ == '__main__':
    unittest.main()

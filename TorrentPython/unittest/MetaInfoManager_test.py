import unittest

from TorrentPython.MetaInfoManager import *

MAGNET_STR = 'magnet:?xt=urn:btih:699CDA895AF6FBD5A817FFF4FE6FA8AB87E36F48'
TORRENT_PATH = '../Resources/cosmos.torrent'


class MetaInfoParserTest(unittest.TestCase):
    def setUp(self):                              
        pass

    def tearDown(self):
        pass

    @unittest.skip("wait")
    def test_parseFromMagnet(self):
        metaInfo = MetaInfoManager.parseFromMagnet(MAGNET_STR)
        self.assertIsNotNone(metaInfo)
        
    @unittest.skip("clear")
    def test_parseFromTorrent(self):
        metaInfo = MetaInfoManager.parseFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(metaInfo)
        self.assertTrue(metaInfo[b'announce'] == b'udp://tracker.openbittorrent.com:80/announce')

    # @unittest.skip("clear")
    def test_getInfoHashFromTorrent(self):
        info_hash = MetaInfoManager.getInfoHashFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(info_hash)
        print(info_hash)

if __name__ == '__main__':
    unittest.main()

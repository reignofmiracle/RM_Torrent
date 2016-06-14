import unittest

from TorrentPython.MetaInfo import *

MAGNET_STR = 'magnet:?xt=urn:btih:699CDA895AF6FBD5A817FFF4FE6FA8AB87E36F48'
SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROOT_TORRENT_PATH = '../Resources/root.torrent'


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
    def test_getInfoHashFromTorrent(self):
        info_hash = MetaInfo.getInfoHashFromTorrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(info_hash)
        print(info_hash)

    # @unittest.skip("clear")
    def test_Metainfo(self):
        metainfo = MetaInfo.createFromTorrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(metainfo.getInfo())
        self.assertEqual(b'http://torrent.ubuntu.com:6969/announce', metainfo.getAnnounce())
        self.assertEqual([[b'http://torrent.ubuntu.com:6969/announce'], [b'http://ipv6.torrent.ubuntu.com:6969/announce']], metainfo.getAnnounceList())
        self.assertEqual(1461232325, metainfo.getCreationDate())
        self.assertEqual(b'Ubuntu CD releases.ubuntu.com', metainfo.getComment())
        self.assertEqual(None, metainfo.getCreatedBy())
        self.assertEqual(None, metainfo.getEncoding())
        self.assertEqual(BaseInfo.FILE_MODE.SINGLE, metainfo.getFileMode())

    # @unittest.skip("clear")
    def test_SingleFileMode(self):
        metainfo = MetaInfo.createFromTorrent(SAMPLE_TORRENT_PATH)
        info = metainfo.getInfo()
        self.assertIsNotNone(info)

        self.assertEqual(BaseInfo.FILE_MODE.SINGLE, info.getFileMode())
        self.assertEqual(b'ubuntu-16.04-server-amd64.iso', info.getName())
        self.assertEqual(686817280, info.getLength())
        self.assertEqual(1310, info.getPieceNum())
        self.assertEqual(524288, info.getPieceLength_index(1309))

    # @unittest.skip("clear")
    def test_MultiFileMode(self):
        metainfo = MetaInfo.createFromTorrent(ROOT_TORRENT_PATH)
        info = metainfo.getInfo()
        self.assertIsNotNone(info)

        self.assertEqual(BaseInfo.FILE_MODE.MULTI, info.getFileMode())
        self.assertEqual(16384, info.getPieceLength())
        self.assertEqual(b'root', info.getName())
        self.assertEqual(6291456, info.getLength())
        self.assertEqual(384, info.getPieceNum())
        self.assertEqual(16384, info.getPieceLength_index(383))

        for file in info.getFiles():
            print(file.getLength(), file.getPath(), file.getFullPath())

if __name__ == '__main__':
    unittest.main()

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
        info_hash = MetaInfo.get_info_hash_from_torrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(info_hash)
        print(info_hash)

    # @unittest.skip("clear")
    def test_Metainfo(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(metainfo.get_info())
        self.assertEqual(b'http://torrent.ubuntu.com:6969/announce', metainfo.get_announce())
        self.assertEqual([[b'http://torrent.ubuntu.com:6969/announce'], [b'http://ipv6.torrent.ubuntu.com:6969/announce']], metainfo.get_announce_list())
        self.assertEqual(1461232325, metainfo.get_creation_date())
        self.assertEqual(b'Ubuntu CD releases.ubuntu.com', metainfo.get_comment())
        self.assertEqual(None, metainfo.get_created_by())
        self.assertEqual(None, metainfo.get_encoding())
        self.assertEqual(BaseInfo.FILE_MODE.SINGLE, metainfo.get_file_mode())

    # @unittest.skip("clear")
    def test_SingleFileMode(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        info = metainfo.get_info()
        self.assertIsNotNone(info)

        self.assertEqual(BaseInfo.FILE_MODE.SINGLE, info.get_file_mode())
        self.assertEqual(b'ubuntu-16.04-server-amd64.iso', info.get_name())
        self.assertEqual(686817280, info.get_length())
        self.assertEqual(1310, info.get_piece_num())
        self.assertEqual(524288, info.get_piece_length_index(1309))

    # @unittest.skip("clear")
    def test_MultiFileMode(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        info = metainfo.get_info()
        self.assertIsNotNone(info)

        self.assertEqual(BaseInfo.FILE_MODE.MULTI, info.get_file_mode())
        self.assertEqual(16384, info.get_piece_length())
        self.assertEqual(b'root', info.get_name())
        self.assertEqual(6291445, info.get_length())
        self.assertEqual(384, info.get_piece_num())
        self.assertEqual(16373, info.get_piece_length_index(383))

        for file in info.iter_files():
            print(file.get_length(), file.get_path())

if __name__ == '__main__':
    unittest.main()

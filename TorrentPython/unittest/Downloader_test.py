import unittest
from TorrentPython.Downloader import Downloader
from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.RoutingTable import RoutingTable
from TorrentPython.TorrentUtils import TorrentUtils

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class DownloaderTest(unittest.TestCase):
    def setUp(self):
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.dest = 'D:/sandbox/'
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_new(self):
        testObj = Downloader(TorrentUtils.getPeerID(), self.metainfo, self.dest, self.routing_table)

        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

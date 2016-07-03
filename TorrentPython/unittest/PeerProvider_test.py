import unittest

from TorrentPython.PeerProvider import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class PeerProviderTest(unittest.TestCase):
    def setUp(self):
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.assertIsNotNone(self.metainfo)
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_get_peers(self):
        testObj = PeerProvider.start(TorrentUtils.getPeerID(), self.metainfo, self.routing_table)
        peer_list = testObj.get_peers(5)
        print(peer_list)

        routing_table = testObj.get_routing_table()
        print(routing_table)

        testObj.stop()
        del testObj

if __name__ == '__main__':
    unittest.main()

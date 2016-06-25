import unittest

from TorrentPython.DHTExplorer import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

SAMPLE_INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class DHTExplorerTest(unittest.TestCase):
    def setUp(self):
        self.info_hash = SAMPLE_INFO_HASH
        # self.addr = ('72.136.88.172', 44822)
        self.addr = RoutingTable.BITTORRENT_NODE_ADDR
        # self.routing_table = RoutingTable.INITIAL_ROUTING_TABLE
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_get_peers(self):
        testObj = DHTExplorer(TorrentUtils.getPeerID(), self.routing_table)
        peer_list, routing_table = testObj.get_peers(self.info_hash, *self.addr)
        self.assertTrue(len(peer_list) > 0 or len(routing_table) > 0)
        print(peer_list)
        print(routing_table)
        del testObj

    # @unittest.skip("clear")
    def test_explore(self):
        testObj = DHTExplorer(TorrentUtils.getPeerID(), self.routing_table)
        peer_list = testObj.explore(self.info_hash, 5, 0)
        self.assertTrue(len(peer_list) > 0)
        print(peer_list)
        print(testObj.routing_table)
        del testObj

    @unittest.skip("clear")
    def test_get_peerout(self):
        testObj = DHTExplorer.get_peerout(5)
        self.assertFalse(testObj(4))
        self.assertTrue(testObj(5))

if __name__ == '__main__':
    unittest.main()

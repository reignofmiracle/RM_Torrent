import unittest

from TorrentPython.PeerDetective import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

SAMPLE_INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'

ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class PeerDetectiveTest(unittest.TestCase):
    def setUp(self):
        self.info_hash = SAMPLE_INFO_HASH
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_find_peers(self):
        testObj = PeerDetective(TorrentUtils.getPeerID(), self.routing_table)
        peer_list = testObj.find_peers(self.info_hash, 5, 0)
        self.assertTrue(len(peer_list) > 0)
        print(peer_list)

        routing_table = testObj.get_routing_table()
        print(routing_table)

        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

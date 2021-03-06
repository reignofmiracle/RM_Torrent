import unittest

from TorrentPython.DHTExplorer import *
from TorrentPython.RoutingTable import *
from TorrentPython.TorrentUtils import *

SAMPLE_INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class DHTExplorerTest(unittest.TestCase):
    def setUp(self):
        self.info_hash = SAMPLE_INFO_HASH
        self.routing_table = RoutingTable.INITIAL_ROUTING_TABLE
        # self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_explore(self):
        testObj = DHTExplorer(TorrentUtils.getPeerID(), self.info_hash, self.routing_table)

        for i in range(100):
            print(len(testObj.routing_table), testObj.routing_table)
            peer_list = testObj.explore(5)
            # self.assertTrue(len(peer_list) > 0)
            print(len(peer_list), peer_list)

        del testObj

    @unittest.skip("clear")
    def test_create_routing_table(self):
        testObj = DHTExplorer(TorrentUtils.getPeerID(), self.info_hash, self.routing_table)

        zero_counter = 0
        for i in range(100):
            print(len(testObj.routing_table), testObj.routing_table)

            peer_list = testObj.explore(self.info_hash, 10, 0)
            print(len(peer_list), peer_list)

            if len(peer_list) == 0:
                zero_counter += 1

                if zero_counter > 20:
                    break

        RoutingTable.save(testObj.routing_table, 'routing_table.py')

        del testObj

if __name__ == '__main__':
    unittest.main()

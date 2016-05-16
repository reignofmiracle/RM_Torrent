import unittest

from TorrentPython.DHTExplorer import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'


class DHTExplorerTest(unittest.TestCase):
    def setUp(self):
        self.routingTable = dict(DHTExplorer.INITIAL_ROUTING_TABLE)
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_findPeers(self):
        DHTService.TIMEOUT_SEC = 0.5 # sec

        service = DHTService()
        peers, routingTable = DHTExplorer.findPeers(service, self.routingTable, INFO_HASH)
        self.assertTrue(len(peers) > 0)
        self.assertTrue(len(routingTable) > 0)

        print(peers)
        print(routingTable)

        pass

    @unittest.skip("clear")
    def test_findPeersFromRoutingTable(self):
        service = DHTService()
        peers, routingTable = DHTExplorer.findPeersFromRoutingTable(
            service, self.routingTable, INFO_HASH,
            DHTExplorer.generatePeerLimitChecker(20),
            DHTExplorer.generateTimeLimitChecker(0))

        self.assertTrue(len(routingTable) > 0)
        print('peers : ', peers)
        print('routingTable : ', routingTable)

if __name__ == '__main__':
    unittest.main()

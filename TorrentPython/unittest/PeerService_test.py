import unittest

from TorrentPython.PeerService import *
from TorrentPython.DHTExplorer import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'

SAMPLE_PEER = ('78.242.206.136', 6136)


class PeerServiceTest(unittest.TestCase):
    def setUp(self):
        # DHTService.TIMEOUT_SEC = 0.5 # sec
        # service = DHTService()
        # peers, routingTable = DHTExplorer.findPeers(service, self.routingTable, INFO_HASH)
        # self.assertTrue(len(peers) > 0)
        self.peer = SAMPLE_PEER
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_handShake(self):
        pass

if __name__ == '__main__':
    unittest.main()

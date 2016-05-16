import unittest

from TorrentPython.PeerService import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
FIRST_PIECE_HASH = b'\x11\x12\xac\x17\x04\xe6JS\x8a\x81\x9a\xa9\x05!m\xf7\x1drpk'
PIECE_LENGTH = 524288
TOTAL_LENGTH = 686817280

SAMPLE_PEER = ('61.228.251.189', 11494)


class PeerServiceTest(unittest.TestCase):
    def setUp(self):
        # DHTService.TIMEOUT_SEC = 0.5 # sec
        # service = DHTService()
        # peers, routingTable = DHTExplorer.findPeers(service, self.routingTable, INFO_HASH)
        # self.assertTrue(len(peers) > 0)
        self.peer = SAMPLE_PEER
        pass

        self.testObj = PeerService(self.peer, INFO_HASH)
        ret = self.testObj.handShake()
        self.assertTrue(ret)

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_handShake(self):
        testObj = PeerService(self.peer, INFO_HASH)
        ret = testObj.handShake()
        self.assertTrue(ret)
        pass

    # @unittest.skip("wait")
    def test_keepAlive(self):
        ret = self.testObj.keepAlive()
        self.assertTrue(ret)
        pass

    # @unittest.skip("wait")
    def test_request(self):
        for idx in range(0, PIECE_LENGTH * 100, PIECE_LENGTH):
            ret = self.testObj.request(0, 0, PIECE_LENGTH)
            self.assertTrue(ret)
        received = self.testObj.recv(1048576)
        print(received)
        pass

if __name__ == '__main__':
    unittest.main()

import unittest
import time

from TorrentPython.PeerService import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
FIRST_PIECE_HASH = b'\x11\x12\xac\x17\x04\xe6JS\x8a\x81\x9a\xa9\x05!m\xf7\x1drpk'
BLOCK_LENGTH = pow(2, 14)
PIECE_LENGTH = 524288
TOTAL_LENGTH = 686817280
BUFFER_LENGTH = pow(2, 15)

SAMPLE_PEER = ('127.0.0.1', 57834)


class PeerServiceTest(unittest.TestCase):
    def setUp(self):
        # DHTService.TIMEOUT_SEC = 0.5 # secs
        # service = DHTService()
        # peers, routingTable = DHTExplorer.findPeers(service, self.routingTable, INFO_HASH)
        # self.assertTrue(len(peers) > 0)
        self.peer = SAMPLE_PEER
        pass

        # self.testObj = PeerService(self.peer, INFO_HASH)
        # ret = self.testObj.handShake()
        # self.assertTrue(ret)
        #
        # ret = self.testObj.interested()
        # self.assertTrue(ret)

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_downloadSequence(self):
        testObj = PeerService(self.peer, INFO_HASH)
        self.assertTrue(testObj.handShake())

        testObj.interested()
        testObj.request(0, 0, 2 ** 14)
        print(testObj.recv(1024))


        # for i in range(1, 10):
        #     testObj.request(i, 0, BLOCK_LENGTH)
        #     time.sleep(10)
        #     print(testObj.recv(BLOCK_LENGTH))


        del testObj

    @unittest.skip("clear")
    def test_handShake(self):
        testObj = PeerService(self.peer, INFO_HASH)
        ret = testObj.handShake()
        self.assertTrue(ret)
        del testObj

    @unittest.skip("clear")
    def test_keepAlive(self):
        ret = self.testObj.keepAlive()
        self.assertTrue(ret)
        pass

    @unittest.skip("clear")
    def test_interested(self):
        ret = self.testObj.interested()
        self.assertTrue(ret)

    @unittest.skip("wait")
    def test_request(self):
        blockIndex = 0
        for offset in range(0, PIECE_LENGTH, BLOCK_LENGTH):
            print(blockIndex)
            blockIndex += 1
            ret = self.testObj.request(20, offset, BLOCK_LENGTH)
            self.assertTrue(ret)
            received = self.testObj.recv(BUFFER_LENGTH)
            print(received)

if __name__ == '__main__':
    unittest.main()

import unittest
import time
import logging
import sys
from TorrentPython.PeerService import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
FIRST_PIECE_HASH = b'\x11\x12\xac\x17\x04\xe6JS\x8a\x81\x9a\xa9\x05!m\xf7\x1drpk'
BLOCK_LENGTH = pow(2, 14)
PIECE_LENGTH = 524288
TOTAL_LENGTH = 686817280
BUFFER_LENGTH = pow(2, 15)

SAMPLE_PEER = ('127.0.0.1', 51413)  # transmission


class PeerServiceTest(unittest.TestCase):
    def setUp(self):
        self.peer = SAMPLE_PEER
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_downloadSequence(self):
        testObj = PeerService.create(self.peer, INFO_HASH)
        self.assertIsNotNone(testObj)

        self.assertTrue(testObj.handShake())

        testObj.unchoke()
        # testObj.interested()

        while True:
            print(testObj.recv(1024))
            time.sleep(3)

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

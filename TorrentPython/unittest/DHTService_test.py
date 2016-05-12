import unittest

from TorrentPython.DHTService import *

import socket

INITIAL_NODE_HOST = 'router.utorrent.com'
INITIAL_NODE_PORT = 6881

INITIAL_NODE_ADDR = (socket.gethostbyname(INITIAL_NODE_HOST), INITIAL_NODE_PORT)

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'


class DHTServiceTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_ping(self):
        testObj = DHTService()
        ret = testObj.ping(INITIAL_NODE_ADDR)
        self.assertIsNotNone(ret)
        self.assertFalse(DHTService.isResponseError(ret))
        pass

    # @unittest.skip("wait")
    def test_getPeers(self):
        testObj = DHTService()
        ret = testObj.getPeers(INITIAL_NODE_ADDR, INFO_HASH)
        self.assertIsNotNone(ret)
        self.assertFalse(DHTService.isResponseError(ret))
        pass

    # @unittest.skip("wait")
    def test_parsePeers(self):
        testObj = DHTService()
        ret = testObj.getPeers(INITIAL_NODE_ADDR, INFO_HASH)
        self.assertIsNotNone(ret)
        self.assertFalse(DHTService.isResponseError(ret))

        if DHTService.isResponseNodes(ret):
            ret = DHTService.parseNodes(ret)
            print(ret)
        else:
            ret = DHTService.parsePeers(ret)
            print(ret)
        pass

if __name__ == '__main__':
    unittest.main()

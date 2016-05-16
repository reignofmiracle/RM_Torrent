import unittest

from TorrentPython.PeerProtocol import *
from TorrentPython.DHTExplorer import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
PIECE_LENGTH = 524288


class PeerProtocolTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_getHandShake(self):
        ret = PeerProtocol.getHandShakeMsg(INFO_HASH, TorrentUtils.getPeerID())
        self.assertIsNotNone(ret)
        pass

    # @unittest.skip("wait")
    def test_getKeepAliveMsg(self):
        ret = PeerProtocol.getKeepAliveMsg()
        self.assertIsNotNone(ret)
        self.assertEqual(b'\x00\x00\x00\x00', ret)
        pass

    # @unittest.skip("wait")
    def test_getRequestMsg(self):
        ret = PeerProtocol.getRequestMsg(0, 0, PIECE_LENGTH)
        self.assertIsNotNone(ret)
        print(ret)
        pass

if __name__ == '__main__':
    unittest.main()

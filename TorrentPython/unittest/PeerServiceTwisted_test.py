import unittest
import logging
import sys
from twisted.internet import reactor

from TorrentPython.PeerServiceTwisted import *
from TorrentPython.TorrentUtils import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'

TRANSMISSION_PORT = 51413


class PeerServiceTwistedTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_PeerServiceProtocolFactory(self):
        reactor.connectTCP('localhost', 51413,
                           PeerServiceProtocolFactory(TorrentUtils.getPeerID(), INFO_HASH))
        reactor.run()

    # @unittest.skip("clear")
    def test_PeerService(self):
        testObj = PeerService('localhost', 51413, INFO_HASH)
        testObj.run()

if __name__ == '__main__':
    unittest.main()

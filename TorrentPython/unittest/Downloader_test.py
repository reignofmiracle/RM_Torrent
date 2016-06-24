import unittest
import socket

UTORRENT_INITIAL_NODE_ID = b'\xeb\xff6isQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
UTORRENT_INITIAL_NODE_IP = '82.221.103.244' #'router.utorrent.com',
UTORRENT_INITIAL_NODE_PORT = 6881
UTORRENT_INITIAL_NODE_ADDR = (socket.gethostbyname(UTORRENT_INITIAL_NODE_IP), UTORRENT_INITIAL_NODE_PORT)

BITTORRENT_INITIAL_NODE_ID = b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
BITTORRENT_INITIAL_NODE_IP = '67.215.246.10' #'router.bittorrent.com'
BITTORRENT_INITIAL_NODE_PORT = 6881
BITTORRENT_INITIAL_NODE_ADDR = (socket.gethostbyname(BITTORRENT_INITIAL_NODE_IP), BITTORRENT_INITIAL_NODE_PORT)

TRANSMISSION_INITIAL_NODE_ID = b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
TRANSMISSION_INITIAL_NODE_IP = '67.215.246.10' #'dht.transmissionbt.com'
TRANSMISSION_INITIAL_NODE_PORT = 6881
TRANSMISSION_INITIAL_NODE_ADDR = (socket.gethostbyname(TRANSMISSION_INITIAL_NODE_IP), TRANSMISSION_INITIAL_NODE_PORT)


class DownloaderTest(unittest.TestCase):
    def setUp(self):
        self.initialNodeAddr = BITTORRENT_INITIAL_NODE_ADDR
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_new(self):
        testObj = DHTService()
        ret = testObj.ping(self.initialNodeAddr)
        self.assertIsNotNone(ret)
        self.assertFalse(DHTService.isResponseError(ret))
        print(ret[b'r'][b'id'])
        pass

if __name__ == '__main__':
    unittest.main()

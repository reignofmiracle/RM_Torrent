import unittest
from TorrentPython.DHTProtocol import *
from TorrentPython.TorrentUtils import *


class DHTProtocolTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_get_ping(self):
        print(DHTProtocol.get_ping(TorrentUtils.getPeerID()))
        pass

if __name__ == '__main__':
    unittest.main()
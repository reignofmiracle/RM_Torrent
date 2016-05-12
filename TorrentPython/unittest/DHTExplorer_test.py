import unittest

from TorrentPython.DHTExplorer import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'


class DHTExplorerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_findPeers(self):
        testObj = DHTExplorer.create()
        self.assertIsNotNone(testObj)
        pass

if __name__ == '__main__':
    unittest.main()

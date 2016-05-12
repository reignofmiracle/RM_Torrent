import unittest
import binascii

from TorrentPython.TrackerManager import *

TORRENT_PATH = '../Resources/sample.torrent'


class TrackerManagerTest(unittest.TestCase):

    def setUp(self):                              
        pass

    def tearDown(self):
        pass

    @unittest.skip("wait")
    def test_requestInfo(self):
        testObj = TrackerManager.CreateFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(testObj)

        ret = testObj.requestInfo()
        self.assertIsNotNone(ret)
        self.assertTrue(type(ret) == dict)

    # @unittest.skip("wait")
    def test_getInfoHash(self):
        testObj = TrackerManager.CreateFromTorrent(TORRENT_PATH)
        self.assertIsNotNone(testObj)

        ret = testObj.getInfoHash()
        print(ret)
        self.assertEqual(20, len(ret))
        self.assertEqual(b'699CDA895AF6FBD5A817FFF4FE6FA8AB87E36F48', binascii.hexlify(ret).upper())

if __name__ == '__main__':
    unittest.main()

import unittest

from TorrentPython.UDPTrackerProtocol import *

import struct

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'
ANNOUNCE = b'udp://tracker.openbittorrent.com:80/announce'


class UDPTrackerProtocolTest(unittest.TestCase):
    def setUp(self):                              
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_ConnectingClass(self):
        testObj = Connecting(0, 0)
        packet = testObj.getPacket()
        self.assertIsNotNone(packet)
        print(packet)

    # @unittest.skip("wait")
    def test_ConnectingResponseClass(self):

        action = 1
        transaction_id = 2
        connection_id = 3
        
        testObj = ConnectingResponse(
            struct.pack('iiq', action, transaction_id, connection_id))
        
        self.assertEqual(action, testObj.action)
        self.assertEqual(transaction_id, testObj.transaction_id)
        self.assertEqual(connection_id, testObj.connection_id)
        
if __name__ == '__main__':
    unittest.main()


import unittest

from TorrentPython.PeerMessage import *


class PeerMessageTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_Message_create(self):
        buf = b'\x00\x00\x00\xa5\x05\xff\xff\xff\xff\xff\xff\xff'
        msg = Message.create(buf)
        self.assertIsNone(msg)

    # @unittest.skip("wait")
    def test_Message_parse(self):
        buf = b'\x00\x00\x00\xa5\x05\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc'
        msg, remain = Message.parse(buf)
        self.assertIsNotNone(msg)
        self.assertEqual(Message.BITFIELD, msg.id)
        self.assertEqual(164, len(msg.bitfield))
        self.assertTrue(msg.have(1310))
        self.assertFalse(msg.have(1311))

if __name__ == '__main__':
    unittest.main()
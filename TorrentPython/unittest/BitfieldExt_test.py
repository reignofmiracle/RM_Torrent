import unittest

from TorrentPython.BitfieldExt import *


class BitfieldExtTest(unittest.TestCase):
    def setUp(self):
        buf = b'\x00\x00\x00\xa5\x05\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc'
        self.msg, remain = Message.parse(buf)
        self.assertIsNotNone(self.msg)
        self.assertEqual(Message.BITFIELD, self.msg.id)

        self.piece_num = 1310
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_create_with_bitfield_message(self):
        testObj = BitfieldExt.create_with_bitfield_message(self.piece_num, self.msg)
        self.assertIsNotNone(testObj)
        self.assertEqual(1310, testObj.get_piece_num())
        self.assertTrue(testObj.have(1309))
        self.assertFalse(testObj.have(1310))
        self.assertEqual(set(), testObj.get_missing_piece_indices())
        self.assertEqual({i for i in range(1310)}, testObj.get_completed_piece_indices())

    # @unittest.skip("clear")
    def test_create_with_missing_piece_indices_None(self):
        testObj = BitfieldExt.create_with_missing_piece_indices(self.piece_num, {1310})
        self.assertIsNone(testObj)

        testObj = BitfieldExt.create_with_missing_piece_indices(-1, {i for i in range(1300)})
        self.assertIsNone(testObj)

    # @unittest.skip("clear")
    def test_create_with_missing_piece_indices(self):
        testObj = BitfieldExt.create_with_missing_piece_indices(self.piece_num, {i for i in range(1300)})
        self.assertIsNotNone(testObj)
        self.assertEqual(1310, testObj.get_piece_num())
        self.assertFalse(testObj.have(1299))
        self.assertTrue(testObj.have(1300))
        self.assertEqual({i for i in range(1300)}, testObj.get_missing_piece_indices())
        self.assertEqual({i for i in range(1300, 1310)}, testObj.get_completed_piece_indices())

    # @unittest.skip("clear")
    def test_create_with_completed_piece_indices(self):
        testObj = BitfieldExt.create_with_completed_piece_indices(self.piece_num, {i for i in range(1300)})
        self.assertIsNotNone(testObj)
        self.assertEqual(1310, testObj.get_piece_num())
        self.assertTrue(testObj.have(1299))
        self.assertFalse(testObj.have(1300))
        self.assertEqual({i for i in range(1300, 1310)}, testObj.get_missing_piece_indices())
        self.assertEqual({i for i in range(1300)}, testObj.get_completed_piece_indices())

if __name__ == '__main__':
    unittest.main()

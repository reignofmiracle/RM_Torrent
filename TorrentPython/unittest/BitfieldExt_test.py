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

    @unittest.skip("clear")
    def test_create_with_bitfield_message(self):
        test_obj = BitfieldExt.create_with_bitfield_message(self.piece_num, self.msg)
        self.assertIsNotNone(test_obj)
        self.assertEqual(1310, test_obj.get_piece_num())
        self.assertTrue(test_obj.have(1309))
        self.assertFalse(test_obj.have(1310))
        self.assertEqual(set(), test_obj.get_missing_piece_indices())
        self.assertEqual({i for i in range(1310)}, test_obj.get_completed_piece_indices())

    @unittest.skip("clear")
    def test_create_with_missing_piece_indices_None(self):
        test_obj = BitfieldExt.create_with_missing_piece_indices(self.piece_num, {1310})
        self.assertIsNone(test_obj)

        test_obj = BitfieldExt.create_with_missing_piece_indices(-1, {i for i in range(1300)})
        self.assertIsNone(test_obj)

    @unittest.skip("clear")
    def test_create_with_missing_piece_indices(self):
        test_obj = BitfieldExt.create_with_missing_piece_indices(self.piece_num, {i for i in range(1300)})
        self.assertIsNotNone(test_obj)
        self.assertEqual(1310, test_obj.get_piece_num())
        self.assertFalse(test_obj.have(1299))
        self.assertTrue(test_obj.have(1300))
        self.assertEqual({i for i in range(1300)}, test_obj.get_missing_piece_indices())
        self.assertEqual({i for i in range(1300, 1310)}, test_obj.get_completed_piece_indices())

    @unittest.skip("clear")
    def test_create_with_completed_piece_indices(self):
        test_obj = BitfieldExt.create_with_completed_piece_indices(self.piece_num, {i for i in range(1300)})
        self.assertIsNotNone(test_obj)
        self.assertEqual(1310, test_obj.get_piece_num())
        self.assertTrue(test_obj.have(1299))
        self.assertFalse(test_obj.have(1300))
        self.assertEqual({i for i in range(1300, 1310)}, test_obj.get_missing_piece_indices())
        self.assertEqual({i for i in range(1300)}, test_obj.get_completed_piece_indices())

    # @unittest.skip("clear")
    def test_create_with_missing_piece_indices(self):

        missing = [900, 1168, 1178, 1306, 1191, 43, 939, 690, 822, 57, 444, 960, 1227, 334, 1231, 721, 471, 474, 1115, 1256, 108, 1260, 635, 1278]
        haves = [635, 690, 474, 57, 1256, 334, 1231, 1306, 1191, 1260, 1168, 43, 900, 108, 444, 1278, 1178, 721, 939, 1115, 471, 822, 1227, 960]

        test_obj = BitfieldExt.create_with_missing_piece_indices(self.piece_num, missing)
        self.assertIsNotNone(test_obj)

        # ret = test_obj.get_missing_piece_indices()
        # self.assertEqual(set(missing), ret)
        #
        # test_obj.set_have(635)
        # self.assertTrue(test_obj.have(635))
        #
        # ret = test_obj.get_missing_piece_indices()
        # self.assertEqual(set(missing) - {635}, ret)
        #
        # test_obj.set_have(690)
        # self.assertTrue(test_obj.have(690))

        for index in haves:
            test_obj.set_have(index)
            if test_obj.have(index) is False:
                print(index)

        self.assertEqual(set(), test_obj.get_missing_piece_indices())

if __name__ == '__main__':
    unittest.main()

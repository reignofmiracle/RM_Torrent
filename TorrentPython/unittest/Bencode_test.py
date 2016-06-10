import unittest

from TorrentPython.Bencode import *

TORRENT_PATH = '../Resources/sample.torrent'


class BencodeTest(unittest.TestCase):
    def setUp(self):
        self.source = None
        with open(TORRENT_PATH, 'rb') as f:
            self.source = f.read()

        self.assertIsNotNone(self.source)
        pass

    def tearDown(self):
        pass    

    # @unittest.skip("wait")
    def test_decode(self):
        ret = Bencode.decode(self.source)        
        self.assertIsNotNone(ret)

        for key in ret:
            print(key)

        # print(b'created by : ', ret[b'created by'])
        print(b'creation date : ', ret[b'creation date'])
        # print(b'encoding : ', ret[b'encoding'])
        print(b'comment : ', ret[b'comment'].decode('UTF-8'))
        print(b'announce : ', ret[b'announce'])
        print(b'announce-list : ', ret[b'announce-list'])

        info = ret[b'info']
        for key in info:
            if key == b'piece length':
                print(key, info[key])
            if key == b'length':
                print(key, info[key])

        # print(b'files : ', info[b'files'])
        print(b'name : ', info[b'name'].decode('UTF-8'))

        # print(info[b'files'][0][b'path'][0].decode('UTF-8'))

    # @unittest.skip("wait")
    def test_getDecoder(self):
        ret = Bencode.getDecoder(self.source, 0)
        self.assertIsNotNone(ret)

    # @unittest.skip("wait")
    def test_decode_s(self):
        ret, npos = Bencode.decode_s(b'4:spam', 0)
        self.assertEqual(b'spam', ret)

        ret, npos = Bencode.decode_s(b'10:abcdefghij', 0)
        self.assertEqual(b'abcdefghij', ret)
        
    # @unittest.skip("wait")
    def test_decode_i(self):
        ret, npos = Bencode.decode_i(b'i12314123e', 0)
        self.assertEqual(12314123, ret)

    # @unittest.skip("wait")
    def test_decode_l(self):
        ret, npos = Bencode.decode_l(b'l4:spam4:eggse', 0)
        self.assertTrue(type(ret) == list)
        self.assertEqual(2, len(ret))
        self.assertEqual(b'spam', ret[0])
        self.assertEqual(b'eggs', ret[1])

    # @unittest.skip("wait")
    def test_decode_d(self):
        ret, npos = Bencode.decode_d(b'd3:cow3:moo4:spam4:eggse', 0)
        self.assertTrue(type(ret) == dict)
        self.assertEqual(2, len(ret))
        self.assertEqual(b'moo', ret[b'cow'])
        self.assertEqual(b'eggs', ret[b'spam'])

        ret, npos = Bencode.decode_d(b'd4:spaml1:a1:bee', 0)
        self.assertTrue(type(ret) == dict)
        self.assertEqual(1, len(ret))

        retList = ret[b'spam']
        self.assertTrue(type(retList) == list)        
        self.assertEqual(b'a', retList[0])
        self.assertEqual(b'b', retList[1])

    # @unittest.skip("wait")
    def test_getInfoBencode(self):
        ret = Bencode.getBencode_Info(self.source)
        self.assertIsNotNone(ret)

    # @unittest.skip("wait")
    def test_encode(self):
        dSource = Bencode.decode(self.source)        
        self.assertIsNotNone(dSource)
        
        ret = Bencode.encode(dSource)
        self.assertIsNotNone(ret)

        self.assertEqual(self.source, ret)

    # @unittest.skip("wait")
    def test_encode_s(self):
        sample = b'4:spam'
        ret, npos = Bencode.decode_s(sample, 0)
        self.assertEqual(b'spam', ret)

        ret = Bencode.encode_s(ret)
        self.assertEqual(sample, ret)

    # @unittest.skip("wait")
    def test_encode_i(self):
        sample = b'i12314123e'
        ret, npos = Bencode.decode_i(sample, 0)
        self.assertEqual(12314123, ret)

        ret = Bencode.encode_i(ret)
        self.assertEqual(sample, ret)

    # @unittest.skip("wait")
    def test_encode_l(self):
        sample = b'l4:spam4:eggse'
        ret, npos = Bencode.decode_l(sample, 0)
        self.assertTrue(type(ret) == list)
        self.assertEqual(2, len(ret))
        self.assertEqual(b'spam', ret[0])
        self.assertEqual(b'eggs', ret[1])

        ret = Bencode.encode_l(ret)
        self.assertEqual(sample, ret)        

    # @unittest.skip("wait")
    def test_encode_d(self):
        sample = b'd3:cow3:moo4:spam4:eggse'
        ret, npos = Bencode.decode_d(sample, 0)
        self.assertTrue(type(ret) == dict)
        self.assertEqual(2, len(ret))
        self.assertEqual(b'moo', ret[b'cow'])
        self.assertEqual(b'eggs', ret[b'spam'])

        ret = Bencode.encode_d(ret)
        self.assertEqual(sample, ret)        

        # test2
        sample = b'd4:spaml1:a1:bee'
        ret, npos = Bencode.decode_d(sample, 0)
        self.assertTrue(type(ret) == dict)
        self.assertEqual(1, len(ret))

        retList = ret[b'spam']
        self.assertTrue(type(retList) == list)        
        self.assertEqual(b'a', retList[0])
        self.assertEqual(b'b', retList[1])

        ret = Bencode.encode_d(ret)
        self.assertEqual(sample, ret)

if __name__ == '__main__':
    unittest.main()

import unittest
import shutil

from TorrentPython.PieceAssembler import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROOT_TORRENT_PATH = '../Resources/root.torrent'


class PieceAssemblerTest(unittest.TestCase):
    def setUp(self):
        self.dest_question = 'D:/sandbox/'
        self.dest_answer = 'D:/sandbox2/'
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_prepare_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(testObj.prepare())
        pass

    @unittest.skip("clear")
    def test_prepare_M(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(testObj.prepare())
        pass

    @unittest.skip("wait")
    def test_get_missing_piece_indices_S_F(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertEqual([i for i in range(0, 384)], testObj.get_missing_piece_Indices())
        pass

    @unittest.skip("wait")
    def test_get_missing_piece_indices_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertEqual([], testObj.get_missing_piece_Indices())
        pass

    @unittest.skip("clear")
    def test_get_missing_piece_indices_M_F(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(testObj.prepare())

        info = metainfo.get_info()
        self.assertEqual([i for i in range(0, info.get_piece_num())], testObj.get_missing_piece_Indices())
        pass

    @unittest.skip("clear")
    def test_get_missing_piece_indices_M_S(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_answer)
        self.assertTrue(testObj.prepare())

        self.assertEqual([], testObj.get_missing_piece_Indices())
        pass

    @unittest.skip("clear")
    def test_get_missing_piece_indices_S_F(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(testObj.prepare())

        info = metainfo.get_info()
        self.assertEqual([i for i in range(0, info.get_piece_num())], testObj.get_missing_piece_Indices())
        pass

    @unittest.skip("clear")
    def test_get_missing_piece_indices_S_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        testObj = PieceAssembler(metainfo, self.dest_answer)
        self.assertTrue(testObj.prepare())
        self.assertEqual([], testObj.get_missing_piece_Indices())
        pass

    # @unittest.skip("clear")
    def test_write_M(self):
        metainfo = MetaInfo.create_from_torrent(ROOT_TORRENT_PATH)
        info = metainfo.get_info()

        if os.path.isdir(self.dest_question + info.get_name().decode()):
            shutil.rmtree(self.dest_question + info.get_name().decode())

        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(testObj.prepare())

        with open(self.dest_answer + 'root_piece_63.raw', 'rb') as f:
            piece_63 = f.read()

        self.assertEqual(16384, len(piece_63))
        self.assertTrue(testObj.write(63, piece_63))

        file_0 = info.get_file(0)
        with open(self.dest_question + file_0.get_full_path().decode(), 'rb') as f:
            f.seek(16384 * 63)
            buf_file_0 = f.read()
            self.assertEqual(buf_file_0, piece_63[:-7])

        file_1 = info.get_file(1)
        with open(self.dest_question + file_1.get_full_path().decode(), 'rb') as f:
            buf_file_1 = f.read()
            self.assertEqual(buf_file_1[:7], piece_63[-7:])

    # @unittest.skip("clear")
    def test_write_S(self):
        metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        info = metainfo.get_info()

        file_path = self.dest_question + info.get_name().decode()
        if os.path.exists(file_path):
            os.remove(file_path)

        testObj = PieceAssembler(metainfo, self.dest_question)
        self.assertTrue(testObj.prepare())

        with open(self.dest_answer + 'sample_piece_1309.raw', 'rb') as f:
            piece_1309 = f.read()

        self.assertEqual(524288, len(piece_1309))
        self.assertTrue(testObj.write(1309, piece_1309))

        with open(self.dest_question + info.get_name().decode(), 'rb') as f:
            f.seek(524288 * 1309)
            buf_file = f.read()
            self.assertEqual(buf_file, piece_1309)

if __name__ == '__main__':
    unittest.main()

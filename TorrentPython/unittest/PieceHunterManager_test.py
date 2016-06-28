import unittest

from TorrentPython.PieceHunterManager import PieceHunterManager


class MetaInfoTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_new(self):
        testObj = PieceHunterManager()
        self.assertIsNotNone(testObj)
        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

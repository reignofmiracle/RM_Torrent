import unittest

from TorrentPython.MetaInfo import *
from TorrentPython.TorrentUtils import *
from TorrentPython.TrackerService import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'


class TrackerManagerTest(unittest.TestCase):

    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.info = self.metainfo.get_info()
        print(self.metainfo.get_announce_list())
        pass

    def tearDown(self):
        pass

    @unittest.skip("wait")
    def test_request(self):
        announce = self.metainfo.get_announce().decode()
        response = Bencode.decode(TrackerService.request(
            announce, self.client_id, self.metainfo.info_hash))
        print(response)

        peers = TrackerProtocol.parse_peers(response)
        self.assertIsNotNone(peers)

        for peer in peers:
            print(peer)

    # @unittest.skip("wait")
    def test_get_peers(self):
        test_obj = TrackerService(self.client_id, self.metainfo)

        while True:
            peers = test_obj.get_peers()
            print(peers)

            if len(peers) == 0:
                break

if __name__ == '__main__':
    unittest.main()

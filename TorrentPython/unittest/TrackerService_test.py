import unittest

from TorrentPython.MetaInfo import *
from TorrentPython.TorrentUtils import *
from TorrentPython.TrackerService import *

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'


class TrackerManagerTest(unittest.TestCase):

    def setUp(self):
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.info = self.metainfo.get_info()
        self.client_id = TorrentUtils.getPeerID()
        print(self.metainfo.get_announce_list())
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_request(self):
        announce = self.metainfo.get_announce().decode()
        response = Bencode.decode(TrackerService.request(
            announce, self.metainfo.info_hash, self.client_id, 6881))
        print(response)

        peers = TrackerProtocol.parse_peers(response)
        self.assertIsNotNone(peers)

        for peer in peers:
            print(peer)

if __name__ == '__main__':
    unittest.main()

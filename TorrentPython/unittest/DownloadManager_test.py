import unittest

from threading import Event
from rx import *

from TorrentPython.DownloadManager import DownloadManager
from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.RoutingTable import RoutingTable
from TorrentPython.TorrentUtils import TorrentUtils

SAMPLE_TORRENT_PATH = '../Resources/sample.torrent'
ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class DownloadManagerTest(unittest.TestCase):
    def setUp(self):
        self.client_id = TorrentUtils.getPeerID()
        self.metainfo = MetaInfo.create_from_torrent(SAMPLE_TORRENT_PATH)
        self.dest = 'D:/sandbox/'
        self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)

    def tearDown(self):
        pass

    @unittest.skip("wait")
    def test_new(self):
        testObj = DownloadManager(self.client_id, self.metainfo, self.dest, self.routing_table)
        testObj.destroy()
        del testObj

    # @unittest.skip("wait")
    def test_update(self):
        testObj = DownloadManager(self.client_id, self.metainfo, self.dest, self.routing_table)
        self.assertIsNotNone(testObj)

        endEvent = Event()

        class DownloadManagerObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg)
                # self.endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                print('on_error')

        testObj.subscribe(DownloadManagerObserver(endEvent))
        testObj.update()

        endEvent.wait()

        testObj.destroy()
        del testObj

if __name__ == '__main__':
    unittest.main()

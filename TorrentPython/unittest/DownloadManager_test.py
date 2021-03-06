import unittest
import filecmp
import time

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
        self.info = self.metainfo.get_info()
        self.dest = 'D:/sandbox/'
        # self.routing_table = RoutingTable.load(ROUTING_TABLE_PATH)
        self.routing_table = None

        self.answer = 'D:/sandbox2/'

    def tearDown(self):
        pass

    @unittest.skip("clear")
    def test_new(self):
        testObj = DownloadManager.start(self.client_id, self.metainfo, self.dest, self.routing_table)
        testObj.stop()
        del testObj

    @unittest.skip("wait")
    def test_on_off(self):
        test_obj = DownloadManager.start(self.client_id, self.metainfo, self.dest, self.routing_table)
        self.assertIsNotNone(test_obj)
        test_obj.subscribe(lambda msg: print(msg))
        test_obj.on()
        time.sleep(10)
        # test_obj.off()
        test_obj.stop()
        del test_obj

    # @unittest.skip("wait")
    def test_download(self):
        testObj = DownloadManager.start(self.client_id, self.metainfo, self.dest, self.routing_table)
        self.assertIsNotNone(testObj)

        endEvent = Event()

        class DownloadManagerObserver(Observer):
            def __init__(self, event):
                self.endEvent = event

            def on_next(self, msg):
                print(msg)
                if msg.bitfield_ext.get_percent() == 100:
                    endEvent.set()

            def on_completed(self):
                print('on_completed')

            def on_error(self, e):
                print('on_error')

        testObj.subscribe(DownloadManagerObserver(endEvent))
        testObj.on()

        endEvent.wait()

        # self.assertTrue(
        #     filecmp.cmp(self.dest + self.info.get_name().decode(),
        #                 self.answer + self.info.get_name().decode()))

        testObj.stop()
        del testObj

if __name__ == '__main__':
    unittest.main()

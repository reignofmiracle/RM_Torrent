from rx.subjects import *
import pykka

from TorrentPython.DownloadManager import *
from TorrentPython.RoutingTable import *


class DownloaderMessage(object):
    IDLE = 'IDLE'
    STATUS = 'STATUS'
    COMPLETED = 'COMPLETED'

    def __init__(self, message_id, message_payload):
        self.id = message_id
        self.payload = message_payload

    @staticmethod
    def idle():
        return DownloaderMessage(DownloaderMessage.IDLE, None)

    @staticmethod
    def status():
        return DownloaderMessage(DownloaderMessage.STATUS, None)

    @staticmethod
    def completed():
        return DownloaderMessage(DownloaderMessage.COMPLETED, None)


class DownloaderActor(pykka.ThreadingActor):

    def __init__(self, downloader):
        super(DownloaderActor, self).__init__()
        self.downloader = downloader
        self.download_manager = DownloadManager(downloader)

    def on_receive(self, message):
        return message.get('func')(self)

    def from_start(self):
        pass

    def from_stop(self):
        pass


class Downloader(Subject):

    def __init__(self, client_id, metainfo, path, routing_table=None):
        super(Downloader, self).__init__()
        self.client_id = client_id
        self.metainfo = metainfo
        self.path = path
        self.routing_table = routing_table or RoutingTable.INITIAL_ROUTING_TABLE
        self.actor = DownloaderActor.start(self)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def start(self):
        self.actor.tell({'func': lambda x: x.from_start()})

    def stop(self):
        self.actor.tell({'func': lambda x: x.from_stop()})



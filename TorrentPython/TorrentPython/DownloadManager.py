import pykka
from rx.subjects import Subject
import threading

from TorrentPython.RoutingTable import *
from TorrentPython.PieceAssembler import *
from TorrentPython.PeerDetective import *
from TorrentPython.PieceHunterManager import *


class DownloadStatus(object):
    pass


class DownloadManagerActor(pykka.ThreadingActor):

    UPDATE_TIMEOUT = 5  # 5 sec

    def __init__(self, downloader_manager, client_id, metainfo, path, routing_table=None):
        super(DownloadManagerActor, self).__init__()
        self.download_manager = downloader_manager
        self.client_id = client_id
        self.metainfo = metainfo
        self.path = path
        self.routing_table = routing_table or RoutingTable.INITIAL_ROUTING_TABLE

        self.info = self.metainfo.get_info()
        self.piece_assembler = PieceAssembler(self.metainfo, self.path)
        self.peer_detective = PeerDetective(self.client_id, self.routing_table)
        self.piece_hunter_manager = PieceHunterManager(self.piece_assembler, self.peer_detective)

        self.last_update = 0
        self.last_missing_piece_indices = None
        self.update_timer = None

    def on_start(self):
        self.piece_assembler.prepare()

    def on_stop(self):
        self.piece_assembler.destroy()
        self.peer_detective.destroy()

    def on_receive(self, message):
        return message.get('func')(self)

    def update(self):
        status = self.get_status()

    def get_status(self, missing_piece_indices):
        pass

    def next_update(self):
        if self.update_timer is not None:
            self.update_timer.cancel()

        self.update_timer = threading.Timer(DownloadManagerActor.UPDATE_TIMEOUT, self.update_async)
        self.update_timer.start()

    def update_async(self):
        if self.actor_ref.is_alive():
            self.actor_ref.tell({'func': lambda x: x.update()})


class DownloadManager(Subject):

    def __init__(self, client_id, metainfo, path, routing_table=None):
        super(DownloadManager, self).__init__()
        self.actor = DownloadManagerActor.start(self, client_id, metainfo, path, routing_table)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def update(self):
        return self.actor.ask({'func': lambda x: x.update()})

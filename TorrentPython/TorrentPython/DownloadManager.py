import pykka
from rx.subjects import Subject
import threading
import copy

from TorrentPython.RoutingTable import *
from TorrentPython.PieceAssembler import *
from TorrentPython.PeerDetective import *
from TorrentPython.HuntingScheduler import *
from TorrentPython.PieceHunterManager import *
from TorrentPython.DownloadStatus import *


class DownloadManagerActor(pykka.ThreadingActor):

    UPDATE_TIMEOUT = 1  # sec
    DOWNLOAD_SPEED_LIMIT = 1024 * 1024 * 10  # 10 MB/s

    FIND_PEER_TIMEOUT = 10  # sec

    PIECE_HUNTER_RECRUIT_SIZE = 5
    PIECE_HUNTER_SIZE_LIMIT = 50

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
        self.hunting_scheduler = HuntingScheduler(self.download_manager, self.piece_assembler)
        self.piece_hunter_manager = PieceHunterManager()

        self.last_update_time = 0
        self.last_bitfield_ext = None
        self.update_timer = None

    def on_start(self):
        self.piece_assembler.prepare()
        self.last_update_time = time.clock()
        self.last_bitfield_ext = self.piece_assembler.get_bitfield_ext()

    def on_stop(self):
        self.piece_assembler.destroy()
        self.peer_detective.destroy()
        self.hunting_scheduler.destroy()
        self.piece_hunter_manager.destroy()

    def on_receive(self, message):
        return message.get('func')(self)

    def update(self):
        status = self.get_status()
        if self.check_expand(status):
            self.expand()
        self.download_manager.on_next(status)
        self.next_update()

    def check_expand(self, status):
        if status.bitfield_ext.is_completed():
            return False

        if status.download_speed >= DownloadManagerActor.DOWNLOAD_SPEED_LIMIT:
            return False

        if self.piece_hunter_manager.size() >= DownloadManagerActor.PIECE_HUNTER_SIZE_LIMIT:
            return False

        return True

    def expand(self):
        peer_list = self.peer_detective.find_peers(
            self.metainfo.info_hash,
            DownloadManagerActor.PIECE_HUNTER_RECRUIT_SIZE,
            DownloadManagerActor.FIND_PEER_TIMEOUT)

        for peer in peer_list:
            piece_hunter = PieceHunter.create(self.hunting_scheduler, self.piece_assembler, *peer)
            if piece_hunter and self.piece_hunter_manager.size() < DownloadManagerActor.PIECE_HUNTER_SIZE_LIMIT:
                self.piece_hunter_manager.register(piece_hunter)

        return True

    def get_status(self):
        current_update_time = time.clock()
        current_bitfield_ext = self.piece_assembler.get_bitfield_ext()

        elapsed_time = current_update_time - self.last_update_time
        current_completed_piece_indices = current_bitfield_ext.get_completed_piece_indices()
        last_completed_piece_indices = self.last_bitfield_ext.get_completed_piece_indices()
        downloaded_piece_indices = current_completed_piece_indices - last_completed_piece_indices
        download_speed = (len(downloaded_piece_indices) * self.info.get_piece_length() / elapsed_time) / 1024 / 1024

        self.last_update_time = current_update_time
        self.last_bitfield_ext = current_bitfield_ext

        return DownloadStatus(copy.deepcopy(current_bitfield_ext), download_speed)

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

import pykka
from rx.core import *
from rx.subjects import *

from TorrentPython.RoutingTable import *
from TorrentPython.PieceAssembler import *
from TorrentPython.PeerProvider import *
from TorrentPython.HuntingScheduler import *
from TorrentPython.PieceHunterManager import *
from TorrentPython.DownloadStatus import *


class DownloadManagerActor(pykka.ThreadingActor):

    DOWNLOAD_INTERVAL = 5  # sec
    DOWNLOAD_SPEED_LIMIT = 1024 * 1024 * 10  # 10 MB/s
    REPORT_INTERVAL = 1  # sec

    FIND_PEER_TIMEOUT = 10  # sec

    PIECE_HUNTER_RECRUIT_SIZE = 10
    PIECE_HUNTER_SIZE_LIMIT = 50

    @staticmethod
    def check_expand(status):
        if status.bitfield_ext.is_completed():
            return False

        if status.download_speed >= DownloadManagerActor.DOWNLOAD_SPEED_LIMIT:
            return False

        if status.peer_size >= DownloadManagerActor.PIECE_HUNTER_SIZE_LIMIT:
            return False

        return True

    def __init__(self, downloader_manager, client_id, metainfo, path, routing_table=None):
        super(DownloadManagerActor, self).__init__()
        self.download_manager = downloader_manager
        self.client_id = client_id
        self.metainfo = metainfo
        self.path = path
        self.routing_table = routing_table or RoutingTable.INITIAL_ROUTING_TABLE

        self.info = self.metainfo.get_info()
        self.piece_assembler = PieceAssembler.start(self.metainfo, self.path)
        self.peer_provider = PeerProvider.start(self.client_id, self.metainfo, self.routing_table)
        self.hunting_scheduler = HuntingScheduler.start(self.piece_assembler)
        self.piece_hunter_manager = PieceHunterManager.start()

        self.download_status = None
        self.status_reporter = None
        self.download_loop = None

    def on_start(self):
        bitfield_ext = self.piece_assembler.get_bitfield_ext()
        download_speed = 0
        peer_list = []
        self.download_status = DownloadStatus(bitfield_ext, download_speed, peer_list)

    def on_stop(self):
        if self.status_reporter:
            self.status_reporter.dispose()
            self.status_reporter = None

        self.piece_assembler.stop()
        self.peer_provider.stop()
        self.hunting_scheduler.stop()
        self.piece_hunter_manager.stop()

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def update_status(self):
        current_bitfield_ext = self.piece_assembler.get_bitfield_ext()
        elapsed_time = DownloadManagerActor.REPORT_INTERVAL
        current_completed_piece_indices = current_bitfield_ext.get_completed_piece_indices()
        last_completed_piece_indices = self.download_status.bitfield_ext.get_completed_piece_indices()
        downloaded_piece_indices = current_completed_piece_indices - last_completed_piece_indices
        download_speed = (len(downloaded_piece_indices) * self.info.get_piece_length() / elapsed_time) / 1024 / 1024
        self.download_status = DownloadStatus(current_bitfield_ext, download_speed, self.piece_hunter_manager.size())
        self.download_manager.on_next(self.download_status)

    def download(self):
        if DownloadManagerActor.check_expand(self.download_status):
            peer_list = self.peer_provider.get_peers(DownloadManagerActor.PIECE_HUNTER_RECRUIT_SIZE)
            print('peer_list', peer_list)

            for peer in peer_list:
                self.piece_hunter_manager.register(PieceHunter.start(
                    self.hunting_scheduler, self.piece_assembler, self.client_id, self.metainfo, *peer))

    def on(self):
        if self.status_reporter is None:
            self.status_reporter = Observable.interval(
                DownloadManagerActor.REPORT_INTERVAL * 1000).subscribe(
                lambda _: self.actor_ref.tell({'func': 'update_status', 'args': None}))

        if self.download_loop is None:
            self.download_loop = Observable.interval(
                DownloadManagerActor.DOWNLOAD_INTERVAL * 1000).subscribe(
                lambda _: self.actor_ref.tell({'func': 'download', 'args': None}))

    def off(self):
        if self.status_reporter:
            self.status_reporter.dispose()
            self.status_reporter = None

        if self.download_loop:
            self.download_loop.dispose()
            self.download_loop = None


class DownloadManager(Subject):

    @staticmethod
    def start(client_id, metainfo, path, routing_table=None):
        return DownloadManager(client_id, metainfo, path, routing_table)

    def __init__(self, client_id, metainfo, path, routing_table=None):
        super(DownloadManager, self).__init__()
        self.actor = DownloadManagerActor.start(self, client_id, metainfo, path, routing_table)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive():
            self.actor.tell({'func': 'stop', 'args': None})

    def on(self):
        self.actor.tell({'func': 'on', 'args': None})

    def off(self):
        self.actor.tell({'func': 'off', 'args': None})

import pykka

from TorrentPython.PieceAssembler import *
from TorrentPython.PeerDetective import *


class DownloadManagerActor(pykka.ThreadingActor):

    def __init__(self, downloader):
        super(DownloadManagerActor, self).__init__()
        self.downloader = downloader
        self.piece_assembler = PieceAssembler(self.downloader.metainfo, self.downloader.path)
        self.peer_detective = PeerDetective(self.downloader.client_id, self.downloader.routing_table)

    def on_stop(self):
        self.piece_assembler.destroy()
        self.peer_detective.destroy()

    def on_receive(self, message):
        return message.get('func')(self)

    def update(self):
        pass


class DownloadManager(object):

    def __init__(self, downloader):
        self.actor = DownloadManagerActor.start(downloader)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def update(self):
        return self.actor.ask({'func': lambda x: x.update()})

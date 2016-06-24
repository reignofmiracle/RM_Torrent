from rx.subjects import *


class Downloader(Subject):

    def __init__(self, client_id, metainfo, dest, routing_table=None):
        super(Downloader, self).__init__()
        self.download_scheduler = None
        self.peer_detective = None
        self.piece_hunter_corporation = None
        self.piece_assembler = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.download_scheduler.destory()
        self.peer_detective.destory()
        self.piece_hunter_corporation.destory()
        self.piece_assembler.destory()



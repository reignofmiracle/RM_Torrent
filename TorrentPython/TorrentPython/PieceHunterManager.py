import pykka

from TorrentPython.PieceHunter import *


class PieceHunterManagerActor(pykka.ThreadingActor):

    def __init__(self):
        super(PieceHunterManagerActor, self).__init__()
        self.piece_hunters = set()

    def on_stop(self):
        for hunter in self.piece_hunters:
            hunter.destroy()

    def on_receive(self, message):
        return message.get('func')(self)

    def size(self):
        return len(self.piece_hunters)

    def register(self, peer_hunter: PieceHunter):
        self.piece_hunters.add(peer_hunter)

    def unregister(self, peer_hunter: PieceHunter):
        self.piece_hunters.remove(peer_hunter)
        peer_hunter.destroy()


class PieceHunterManager(object):

    def __init__(self):
        self.core = PieceHunterManagerActor.start()

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.core.is_alive():
            self.core.stop()

    def size(self):
        return self.core.ask({'func': lambda x: x.size()})

    def register(self, piece_hunter: PieceHunter):
        self.core.tell({'func': lambda x: x.register(piece_hunter)})

    def unregister(self, piece_hunter: PieceHunter):
        self.core.tell({'func': lambda x: x.unregister(piece_hunter)})

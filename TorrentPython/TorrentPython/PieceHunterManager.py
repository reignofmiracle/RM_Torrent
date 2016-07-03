import pykka

from TorrentPython.PieceHunter import *


class PieceHunterManagerActor(pykka.ThreadingActor):

    def __init__(self):
        super(PieceHunterManagerActor, self).__init__()
        self.piece_hunters = {}

    def on_stop(self):
        for hunter in self.piece_hunters:
            hunter.stop()

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def size(self):
        return len(self.piece_hunters)

    def register(self, peer_hunter: PieceHunter):
        if peer_hunter:
            self.piece_hunters[peer_hunter.get_uid()] = peer_hunter
            peer_hunter.subscribe(
                on_completed=lambda: self.actor_ref.tell({'func': 'unregister', 'args': (peer_hunter,)}))
            peer_hunter.connect()

    def unregister(self, peer_hunter: PieceHunter):
        if peer_hunter:
            self.piece_hunters.pop(peer_hunter.get_uid())
            peer_hunter.stop()


class PieceHunterManager(object):

    @staticmethod
    def start():
        return PieceHunterManager()

    def __init__(self):
        self.core = PieceHunterManagerActor.start()

    def __del__(self):
        self.stop()

    def stop(self):
        if self.core.is_alive():
            self.core.stop()

    def size(self):
        return self.core.ask({'func': 'size', 'args': None})

    def register(self, piece_hunter: PieceHunter):
        self.core.tell({'func': 'register', 'args': (piece_hunter,)})

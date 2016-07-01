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
        return message.get('func')(self)

    def size(self):
        return len(self.piece_hunters)

    def register(self, peer_hunter: PieceHunter):
        if peer_hunter:
            # print('connect', peer_hunter.get_uid())
            if peer_hunter.connect() is True:
                print('register', peer_hunter.get_uid())
                peer_hunter.subscribe(
                    on_completed=lambda: self.actor_ref.tell({'func': lambda x: x.unregister(peer_hunter)}))
                self.piece_hunters[peer_hunter.get_uid()] = peer_hunter
                print('PieceHunter.size', len(self.piece_hunters))
            else:
                # print('connection failed', peer_hunter.get_uid())
                peer_hunter.destroy()

    def unregister(self, peer_hunter: PieceHunter):
        if peer_hunter:
            print('unregister', peer_hunter.get_uid())
            self.piece_hunters.pop(peer_hunter.get_uid())
            peer_hunter.destroy()
            print('PieceHunter.size', len(self.piece_hunters))


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

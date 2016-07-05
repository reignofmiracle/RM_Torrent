import pykka

from TorrentPython.PieceHunter import *


class PieceHunterManagerActor(pykka.ThreadingActor):

    def __init__(self):
        super(PieceHunterManagerActor, self).__init__()
        self.piece_hunters = {}

    def on_stop(self):
        for uid in self.piece_hunters:
            hunter = self.piece_hunters[uid]
            hunter.stop()

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def size(self):
        return len(self.piece_hunters)

    def register(self, peer_hunter: PieceHunter):
        if peer_hunter:
            print('register', peer_hunter.get_uid())
            self.piece_hunters[peer_hunter.get_uid()] = peer_hunter

    def unregister(self, peer_hunter: PieceHunter):
        if peer_hunter:
            uid = peer_hunter.get_uid()
            peer_hunter.stop()

            if uid in self.piece_hunters:
                self.piece_hunters.pop(uid)
                print('unregister', uid)

    def from_register(self, peer_hunter: PieceHunter):
        if peer_hunter:
            if peer_hunter.get_uid() in self.piece_hunters:
                peer_hunter.stop()
            else:
                def register_at_connected(msg):
                    if msg.get('id') == 'connected':
                        self.actor_ref.tell({'func': 'register', 'args': (peer_hunter,)})
                peer_hunter.subscribe(
                    on_next=register_at_connected,
                    on_completed=lambda: self.actor_ref.tell({'func': 'unregister', 'args': (peer_hunter,)}))
                peer_hunter.connect()


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
        self.core.tell({'func': 'from_register', 'args': (piece_hunter,)})

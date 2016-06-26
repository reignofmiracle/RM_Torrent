import pykka

from TorrentPython.PieceRadio import PieceRadio


class PieceHunterManagerActor(pykka.ThreadingActor):

    def __init__(self, piece_assembler, peer_detective):
        super(PieceHunterManagerActor, self).__init__()
        self.piece_assembler = piece_assembler
        self.peer_detective = peer_detective
        self.piece_hunters = []

    def on_receive(self, message):
        return message.get('func')(self)

    def expand(self):
        pass


class PieceHunterManager(object):

    def __init__(self, piece_assembler, peer_detective):
        self.core = PieceHunterManagerActor.start(piece_assembler, peer_detective)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.core.is_alive():
            self.core.stop()

    def expand(self):
        return self.core.ask({'func': lambda x: x.expand()})

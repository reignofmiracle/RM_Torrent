import pykka

from TorrentPython.PieceRadio import PieceRadio


class PieceHunterCorporationCore(pykka.ThreadingActor):

    def __init__(self):
        super(PieceHunterCorporationCore, self).__init__()
        self.piece_hunters = []

    def on_receive(self, message):
        return message.get('func')(self)

    def register(self, piece_hunter: PieceRadio):
        pass

    def register(self, piece_hunter: PieceRadio):
        pass


class PieceHunterCorporation(object):

    def __init__(self):
        self.core = PieceHunterCorporationCore.start()

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.core.is_alive():
            self.core.stop()

    def register(self, piece_hunter: PieceRadio):
        return self.core.ask({'func': lambda x: x.register(piece_hunter)})

    def unregister(self, piece_hunter: PieceRadio):
        return self.core.ask({'func': lambda x: x.unregister(piece_hunter)})




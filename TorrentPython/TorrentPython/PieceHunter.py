

class PieceHunter(object):

    @staticmethod
    def create(hunting_scheduler, piece_assembler, peer_ip, peer_port):
        pass

    def __init__(self):
        self.piece_radio = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.piece_radio:
            self.piece_radio.destroy()
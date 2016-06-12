from TorrentPython.PeerRadio import *


class PieceHunter(object):

    @staticmethod
    def create(client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port):
        peerRadio = PeerRadio.create(client_id, metainfo, peer_ip, peer_port)
        if peerRadio is None:
            return None

        return PieceHunter(peerRadio)

    def __init__(self, peerRadio: PeerRadio):
        self.peerRadio = peerRadio
        self.metainfo = peerRadio.metainfo

    def __del__(self):
        if self.peerRadio is not None:
            del self.peerRadio
            self.peerRadio = None

    def hunt(self, piece_observer, piece_indices: list, piece_per_step):
        if piece_observer is None or len(piece_indices) == 0 or piece_per_step < 1:
            return None

        return PiecePrize(self, piece_observer, piece_indices, piece_per_step)


class PiecePrize(Subject):
    PIECE_PER_STEP = 5
    INVALID_PIECE_INDEX = -1

    def __init__(self, pieceHunter: PieceHunter, piece_observer, piece_indices: list, piece_per_step):
        super(PiecePrize, self).__init__()
        self.pieceHunter = pieceHunter
        self.peerRadio = pieceHunter.peerRadio
        self.metaInfo = pieceHunter.metainfo
        self.piece_indices = piece_indices
        self.piece_per_step = piece_per_step
        self.subscribe(piece_observer)

        self.msgSubscription = self.peerRadio.subscribe(on_next=self.in_next, on_completed=self.in_completed)

        self.piece_queue = piece_indices.copy()
        self.workingPiece_index = PiecePrize.INVALID_PIECE_INDEX
        self.workingPiece = b''
        self.workingStep = 0

        if not self.peerRadio.chock:
            self.request()

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if self.msgSubscription is not None:
            self.msgSubscription.dispose()
            self.msgSubscription = None

    def in_next(self, msg):
        if msg.id == Message.UNCHOCK:
            self.request()

        if msg.id == Message.PIECE:
            self.update(msg)

    def in_completed(self):
        self.out_error('peer radio off.')

    def out_next(self, value):
        self.on_next(value)

    def out_completed(self):
        self.cleanup()
        self.on_completed()

    def out_error(self, reason):
        self.cleanup()
        self.on_error(Exception(reason))

    def request(self):
        if len(self.piece_queue) > 0:
            if int(len(self.piece_queue) / self.piece_per_step) > 0:
                self.workingStep = self.piece_per_step
            else:
                self.workingStep = len(self.piece_queue) % self.piece_per_step

            for i in range(0, self.workingStep):
                index = self.piece_queue[i]
                print('request : ', index)

                piece_length = self.metaInfo.getPieceLength(index)

                block_num = int(piece_length / PeerRadio.BLOCK_SIZE)
                block_remain = piece_length % PeerRadio.BLOCK_SIZE
                for j in range(0, block_num):
                    self.peerRadio.request(index, j * PeerRadio.BLOCK_SIZE, PeerRadio.BLOCK_SIZE)
                if block_remain > 0:
                    self.peerRadio.request(index, block_num * PeerRadio.BLOCK_SIZE, block_remain)

    def update(self, msg: Piece):
        if msg.index == self.workingPiece_index:
            if msg.begin == len(self.workingPiece):
                self.workingPiece += msg.block
            else:
                self.out_error('piece middle error.')
                return False

            expectLength = self.metaInfo.getPieceLength(self.workingPiece_index)
            if expectLength == len(self.workingPiece):
                self.out_next((self.workingPiece_index, self.workingPiece))
                self.piece_queue.remove(self.workingPiece_index)

                self.workingPiece_index = PiecePrize.INVALID_PIECE_INDEX
                self.workingPiece = b''

                if len(self.piece_queue) == 0:
                    self.out_completed()
                else:
                    self.workingStep -= 1
                    if self.workingStep == 0:
                        self.request()
        else:
            if self.workingPiece_index == PiecePrize.INVALID_PIECE_INDEX:
                if msg.begin == 0:
                    self.workingPiece_index = msg.index
                    self.workingPiece = msg.block
                else:
                    self.out_error('piece beginning error.')
                    return False
            else:
                self.out_error('piece unexpected beginning error.')
                return False

        return True

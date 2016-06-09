from rx import *
from rx.subjects import *
import socket
from threading import Thread

from TorrentPython.MetaInfo import *
from TorrentPython.PeerMessage import *


class PieceDownloader(ReplaySubject):

    KEEP_ALIVE_TIMEOUT = 20
    BLOCK_SIZE = 2 ** 14
    BUFFER_SIZE = BLOCK_SIZE + 13  # 4 + 1 + 4 + 4

    @staticmethod
    def create(client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port, piece_indices: list):
        if piece_indices is None or len(piece_indices) is 0:
            return None

        ret = PieceDownloader(client_id, metainfo, peer_ip, peer_port, piece_indices)
        if not ret.handshake():
            return None

        return ret

    def __init__(self, client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port, piece_indices: list):
        super(PieceDownloader, self).__init__(len(piece_indices) * 2)
        self.client_id = client_id
        self.metainfo = metainfo
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.piece_indices = piece_indices

        self.sock = None
        self.keepAliveSubscription = None
        self.recvSubscription = None
        self.remain = b''
        self.chock = True
        self.bitfield = None
        self.target_piece_index = None
        self.target_piece_begin = None
        self.target_piece = None
        self.target_piece_len = None
        self.completed_piece_indices = []

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

        if self.keepAliveSubscription is not None:
            self.keepAliveSubscription.unsubscribe()
            self.keepAliveSubscription = None

        if self.recvSubscription is not None:
            self.recvSubscription.unsubscribe()
            self.recvSubscription = None

    def handshake(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.peer_ip, self.peer_port))
        except:
            return False

        buf = Handshake.getBytes(self.metainfo.info_hash, self.client_id)
        if buf is None:
            return False

        self.sock.send(buf)
        received = self.sock.recv(Handshake.TOTAL_LEN)

        msg = Handshake.create(received)
        if msg is None or msg.info_hash != self.metainfo.info_hash:
            return False

        self.keepAliveSubscription = Observable.interval(
            PieceDownloader.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keepAlive())

        self.th = Thread(target=PieceDownloader.recvThread, args=(self,))
        self.th.daemon = True
        self.th.start()

        return True

    def keepAlive(self):
        self.sock.send(KeepAlive.getBytes())

    @staticmethod
    def recvThread(pieceDownloader):
        try:
            while True:
                pieceDownloader.handle(pieceDownloader.recv(PieceDownloader.BUFFER_SIZE))
        except:
            pass

    def recv(self, bufsize):
        return self.sock.recv(bufsize)

    def handle(self, buf):
        buf = self.remain + buf
        while True:
            msg, buf = Message.parse(buf)
            if msg is None:
                break
            else:
                print('Received : ', msg)
                self.update(msg)

        self.remain = buf

    def update(self, msg: Message):
        if msg.id == Message.CHOCK:
            self.chock = True
        if msg.id == Message.UNCHOCK:
            self.chock = False
            self.interested()
            self.request()

        if msg.id == Message.BITFIELD:
            self.bitfield = msg

        if msg.id == Message.PIECE:
            self.updatePiece(msg)
            self.request()

        if msg.id == Message.CANCEL:
            self.completed()

    def interested(self):
        msg = Interested.getBytes()
        self.sock.send(msg)

    def request(self):
        if self.chock is True or self.bitfield is None:
            return False

        if self.target_piece is None:

            if len(self.piece_indices) is 0:
                return False

            self.target_piece_index = self.piece_indices.pop()
            self.target_piece_begin = 0
            self.target_piece = b''

            if self.target_piece_index is self.metainfo.getInfoPieceNum() - 1:
                self.target_piece_len = self.metainfo.getInfoLength() % self.metainfo.getInfoPieceLength()
                if self.target_piece_len is 0:
                    self.target_piece_len = self.metainfo.getInfoPieceLength()
            else:
                self.target_piece_len = self.metainfo.getInfoPieceLength()

        msg = Request.getBytes(self.target_piece_index, self.target_piece_begin, PieceDownloader.BLOCK_SIZE)
        self.sock.send(msg)

        return True

    def updatePiece(self, msg: Piece):
        if msg is None:
            return False

        self.target_piece_begin = msg.begin + len(msg.block)
        self.target_piece += msg.block

        if len(self.target_piece) == self.target_piece_len:

            self.on_next((self.target_piece_index, self.target_piece))
            self.completed_piece_indices.append(self.target_piece_index)

            self.target_piece_index = None
            self.target_piece_begin = None
            self.target_piece = None
            self.target_piece_len = None

        return True

    def completed(self):
        self.cleanup()
        self.on_completed()












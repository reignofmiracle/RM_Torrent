from rx import *
from rx.subjects import *
import socket
from threading import *

from TorrentPython.MetaInfo import *
from TorrentPython.PeerMessage import *


class PeerRadio(Subject):
    SOCKET_TIMEOUT = 10
    KEEP_ALIVE_TIMEOUT = 5
    BLOCK_SIZE = 2 ** 14
    BUFFER_SIZE = BLOCK_SIZE + 13  # 4 + 1 + 4 + 4

    @staticmethod
    def create(client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port):
        ret = PeerRadio(client_id, metainfo, peer_ip, peer_port)
        if not ret.handshake():
            return None

        return ret

    @staticmethod
    def recvThread(owner):
        while True:
            try:
                owner.handle(owner.recv(PeerRadio.BUFFER_SIZE))
            except socket.timeout:
                pass
            except:
                owner.out_complete()

    def __init__(self, client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port):
        super(PeerRadio, self).__init__()
        self.client_id = client_id
        self.metainfo = metainfo
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.sock = None
        self.keepAliveSubscription = None
        self.remain = b''
        self.chock = True
        self.bitfield = None

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

        if self.keepAliveSubscription is not None:
            self.keepAliveSubscription.dispose()
            self.keepAliveSubscription = None

    def recv(self, buffersize):
        return self.sock.recv(buffersize)

    def handle(self, buf):
        buf = self.remain + buf
        while True:
            msg, buf = Message.parse(buf)
            if msg is None:
                break
            else:
                self.out_next(msg)

        self.remain = buf

    def out_next(self, msg: Message):
        if msg.id == Message.CHOCK:
            self.chock = True
            self.on_next(msg)

        if msg.id == Message.UNCHOCK:
            self.chock = False
            self.interested()
            self.on_next(msg)

        if msg.id == Message.PIECE:
            self.on_next(msg)

        if msg.id == Message.BITFIELD:
            self.bitfield = msg
            self.on_next(msg)

        if msg.id == Message.CANCEL:
            self.out_complete()

    def out_complete(self):
        self.cleanup()
        self.on_completed()

    def handshake(self):
        buf = Handshake.getBytes(self.metainfo.info_hash, self.client_id)
        if buf is None:
            return False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(PeerRadio.SOCKET_TIMEOUT)
            self.sock.connect((self.peer_ip, self.peer_port))
            self.sock.send(buf)
            received = self.sock.recv(Handshake.TOTAL_LEN)
        except:
            return False

        msg = Handshake.create(received)
        if msg is None or msg.info_hash != self.metainfo.info_hash:
            return False

        self.keepAliveSubscription = Observable.interval(
            PeerRadio.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keepAlive())

        th = Thread(target=PeerRadio.recvThread, args=(self,))
        th.daemon = True
        th.start()

        return True

    def keepAlive(self):
        self.sock.send(KeepAlive.getBytes())

    def interested(self):
        if self.chock:
            return False

        self.sock.send(Interested.getBytes())
        return True

    def request(self, index, begin, length):
        if self.chock:
            return False

        if length <= 0:
            return False

        self.sock.send(Request.getBytes(index, begin, PeerRadio.BLOCK_SIZE))
        return True

    def have(self, index):
        self.sock.send(Have.getBytes(index))



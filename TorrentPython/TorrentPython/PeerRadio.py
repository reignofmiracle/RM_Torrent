from rx.core import *
from rx.subjects import *
import pykka
import socket
from threading import Thread

from TorrentPython.MetaInfo import *
from TorrentPython.PeerMessage import *


class PeerRadioCore(pykka.ThreadingActor):
    SOCKET_TIMEOUT = 3
    KEEP_ALIVE_TIMEOUT = 60
    BLOCK_SIZE = 2 ** 14
    BUFFER_SIZE = BLOCK_SIZE + 13  # 4 + 1 + 4 + 4

    @staticmethod
    def recvThread(owner):
        while True:
            try:
                owner.handle(owner.recv(PeerRadioCore.BUFFER_SIZE))
            except socket.timeout:
                pass
            except:
                owner.on_completed()
                break

    def __init__(self, peer_radio, client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port):
        super(PeerRadioCore, self).__init__()
        self.peer_radio = peer_radio
        self.client_id = client_id
        self.metainfo = metainfo
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.sock = None
        self.keepAliveSubscription = None
        self.remain = b''
        self.chock = True
        self.bitfield = None

    def on_start(self):
        if not self.handshake():
            self.peer_radio.on_completed()

    def on_stop(self):
        if self.sock:
            self.sock.close()
            self.sock = None

        if self.keepAliveSubscription:
            self.keepAliveSubscription.dispose()
            self.keepAliveSubscription = None

    def on_receive(self, message):
        try:
            func_name = message.get('func_name')
            args = message.get('args')
            if func_name and args:
                return getattr(self, func_name)(*args) if len(args) > 0 else getattr(self, func_name)()
        except:
            pass

        return None

    def recv(self, buffersize):
        return self.sock.recv(buffersize)

    def send(self, buf):
        return self.sock.send(buf)

    def handle(self, buf):
        buf = self.remain + buf
        while True:
            msg, buf = Message.parse(buf)
            if msg is None:
                break
            else:
                self.on_next(msg)

        self.remain = buf

    def on_next(self, msg: Message):
        if msg.id == Message.CHOCK:
            self.tell({'func_name': 'set_chock', 'args': (True,)})
            self.peer_radio.on_next(msg)

        if msg.id == Message.UNCHOCK:
            self.tell({'func_name': 'set_chock', 'args': (False,)})
            self.interested()
            self.peer_radio.on_next(msg)

        if msg.id == Message.PIECE:
            self.peer_radio.on_next(msg)

        if msg.id == Message.BITFIELD:
            self.bitfield = msg

        if msg.id == Message.CANCEL:
            self.peer_radio.on_completed()

    def on_completed(self):
        self.peer_radio.on_completed()

    def handshake(self):
        buf = Handshake.getBytes(self.metainfo.info_hash, self.client_id)
        if buf is None:
            return False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(PeerRadioCore.SOCKET_TIMEOUT)
            self.sock.connect((self.peer_ip, self.peer_port))
            self.sock.send(buf)
            received = self.sock.recv(Handshake.TOTAL_LEN)
        except:
            return False

        msg = Handshake.create(received)
        if msg is None or msg.info_hash != self.metainfo.info_hash:
            return False

        self.keepAliveSubscription = Observable.interval(
            PeerRadioCore.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keepAlive())

        th = Thread(target=PeerRadioCore.recvThread, args=(self,))
        th.daemon = True
        th.start()

        return True

    def keepAlive(self):
        return self.send(KeepAlive.getBytes())

    def interested(self):
        return self.send(Interested.getBytes()) if not self.chock else False

    def request(self, index, begin, length):
        if not self.chock and 0 < length <= PeerRadio.BLOCK_SIZE:
            try:
                self.send(Request.getBytes(index, begin, PeerRadio.BLOCK_SIZE))
                return True
            except:
                return False
        else:
            return False

    def get_bitfield(self):
        return self.bitfield

    def set_chock(self, value):
        self.chock = value


class PeerRadio(Subject):

    def __init__(self, client_id: bytes, metainfo: MetaInfo, peer_ip, peer_port):
        super(PeerRadio, self).__init__()
        self.core = PeerRadioCore.start(self, client_id, metainfo, peer_ip, peer_port)

    def __del__(self):
        self.core.stop()

    def request(self, index, begin, length):
        return self.core.ask({'func_name': 'request', 'args': (index, begin, length)})

    def get_bitfield(self):
        return self.core.ask({'func_name': 'get_bitfield', 'args': None})






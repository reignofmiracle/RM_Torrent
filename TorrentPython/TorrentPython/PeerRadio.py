from rx.core import *
from rx.subjects import *
import pykka
import socket
from threading import Thread
import logging

from TorrentPython.MetaInfo import *
from TorrentPython.PeerMessage import *


class PeerRadioMessage(object):
    CONNECTED = 'CONNECTED'
    DISCONNECTED = 'DISCONNECTED'
    RECEIVED = 'RECEIVED'

    def __init__(self, message_id, message_payload):
        self.id = message_id
        self.payload = message_payload

    @staticmethod
    def connected():
        return PeerRadioMessage(PeerRadioMessage.CONNECTED, None)

    @staticmethod
    def disconnected():
        return PeerRadioMessage(PeerRadioMessage.DISCONNECTED, None)

    @staticmethod
    def received(message):
        return PeerRadioMessage(PeerRadioMessage.RECEIVED, message)


class PeerRadioActor(pykka.ThreadingActor):
    SOCKET_TIMEOUT = 5
    KEEP_ALIVE_TIMEOUT = 60
    BLOCK_SIZE = 2 ** 14
    BUFFER_SIZE = BLOCK_SIZE + 13  # 4 + 1 + 4 + 4

    @staticmethod
    def recvThread(owner):
        while True:
            try:
                owner.handle(owner.recv(PeerRadioActor.BUFFER_SIZE))
            except socket.timeout:
                pass
            except Exception as e:
                logging.debug(e)
                owner.error()
                break

    def __init__(self, peer_radio, client_id: bytes, metainfo: MetaInfo):
        super(PeerRadioActor, self).__init__()
        self.peer_radio = peer_radio
        self.client_id = client_id
        self.metainfo = metainfo

        self.sock = None
        self.keepAliveSubscription = None
        self.connected = False

        self.remain = b''
        self.chock = True

    def on_start(self):
        pass

    def on_stop(self):
        self.disconnect()
        self.peer_radio.on_completed()

    def on_receive(self, message):
        return message.get('func')(self)

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

    def error(self):
        if self.actor_ref.is_alive():
            self.actor_ref.tell({'func': lambda x: x.disconnect()})

    def on_next(self, msg: Message):
        if msg.id == Message.CHOCK:
            self.actor_ref.tell({'func': lambda x: x.set_chock(True)})
            self.peer_radio.on_next(PeerRadioMessage.received(msg))

        elif msg.id == Message.UNCHOCK:
            self.interested()
            self.actor_ref.tell({'func': lambda x: x.set_chock(False)})
            self.peer_radio.on_next(PeerRadioMessage.received(msg))

        elif msg.id == Message.PIECE:
            self.peer_radio.on_next(PeerRadioMessage.received(msg))

        elif msg.id == Message.BITFIELD:
            self.peer_radio.on_next(PeerRadioMessage.received(msg))

    def keep_alive(self):
        return self.send(KeepAlive.getBytes())

    def interested(self):
        return self.send(Interested.getBytes())

    def set_chock(self, value):
        self.chock = value

    def connect(self, peer_ip, peer_port):
        if self.connected is True:
            return False

        buf = Handshake.getBytes(self.metainfo.info_hash, self.client_id)
        if buf is None:
            return False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(PeerRadioActor.SOCKET_TIMEOUT)
            self.sock.connect((peer_ip, peer_port))
            self.sock.send(buf)
            received = self.sock.recv(Handshake.TOTAL_LEN)
        except:
            return False

        msg = Handshake.create(received)
        if msg is None or msg.info_hash != self.metainfo.info_hash:
            return False

        self.keepAliveSubscription = Observable.interval(
            PeerRadioActor.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keep_alive())

        th = Thread(target=PeerRadioActor.recvThread, args=(self,))
        th.daemon = True
        th.start()

        self.connected = True
        self.remain = b''
        self.chock = True

        self.peer_radio.on_next(PeerRadioMessage.connected())
        return True

    def disconnect(self):
        if not self.connected:
            return False

        if self.keepAliveSubscription:
            self.keepAliveSubscription.dispose()
            self.keepAliveSubscription = None

        if self.sock:
            self.sock.close()
            self.sock = None

        self.connected = False
        self.remain = b''
        self.chock = True

        self.peer_radio.on_next(PeerRadioMessage.disconnected())
        return True

    def request(self, index, begin, length):
        if not self.connected:
            return False

        if not self.chock and 0 < length <= PeerRadioActor.BLOCK_SIZE:
            try:
                self.send(Request.getBytes(index, begin, length))
                return True
            except:
                return False
        else:
            return False

    def getChock(self):
        return self.chock


class PeerRadio(Subject):
    def __init__(self, client_id: bytes, metainfo: MetaInfo):
        super(PeerRadio, self).__init__()
        self.actor = PeerRadioActor.start(self, client_id, metainfo)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def connect(self, peer_ip, peer_port):
        return self.actor.ask({'func': lambda x: x.connect(peer_ip, peer_port)})

    def disconnect(self):
        return self.actor.ask({'func': lambda x: x.disconnect()})

    def request(self, index, begin, length):
        return self.actor.ask({'func': lambda x: x.request(index, begin, length)})

    def get_chock(self):
        return self.actor.ask({'func': lambda x: x.get_chock()})

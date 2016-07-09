import copy

import pykka
from rx.core import *
from rx.subjects import *
from threading import Thread
import socket
import logging

from TorrentPython.MetaInfo import *
from TorrentPython.BitfieldExt import *
from TorrentPython.PeerMessage import *


class PeerRadioActor(pykka.ThreadingActor):
    SOCKET_TIMEOUT = 5
    KEEP_ALIVE_TIMEOUT = 60
    BLOCK_SIZE = 2 ** 14
    BUFFER_SIZE = BLOCK_SIZE + 13  # 4 + 1 + 4 + 4

    @staticmethod
    def recv_main(peer_radio_actor):
        while peer_radio_actor.connected:
            try:
                peer_radio_actor.on_update(peer_radio_actor.recv(PeerRadioActor.BUFFER_SIZE))
            except socket.timeout:
                pass
            except Exception as e:
                print(e, peer_radio_actor.sock)
                if peer_radio_actor.actor_ref.is_alive():
                    peer_radio_actor.actor_ref.tell({'func': 'on_disconnected', 'args': None})
                return

    def __init__(self, peer_radio, client_id: bytes, metainfo: MetaInfo):
        super(PeerRadioActor, self).__init__()
        self.peer_radio = peer_radio
        self.client_id = client_id
        self.metainfo = metainfo
        self.info = self.metainfo.get_info()

        self.connected = False

        self.sock = None
        self.recv_main_thread = None
        self.keep_alive_subscription = None

        self.remain = b''
        self.chock = True

    def cleanup(self):
        if self.sock:
            self.sock.close()
            self.sock = None

        self.recv_main_thread = None

        if self.keep_alive_subscription:
            self.keep_alive_subscription.dispose()
            self.keep_alive_subscription = None

        self.remain = b''
        self.chock = True

    def recv(self, buffersize):
        return self.sock.recv(buffersize)

    def send(self, buf):
        try:
            self.sock.send(buf)
            return True
        except:
            return False

    def on_stop(self):
        self.disconnect()
        self.peer_radio.on_completed()

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def on_disconnected(self):
        self.connected = False
        self.cleanup()
        self.peer_radio.on_next({'id': 'disconnected', 'payload': None})

    def on_update(self, buf):
        buf = self.remain + buf
        while True:
            msg, buf = Message.parse(buf)
            if msg is None:
                break
            else:
                self.actor_ref.tell({'func': 'on_next', 'args': (msg,)})

        self.remain = buf

    def on_next(self, msg):
        # print(msg)

        if msg.id == Message.CHOCK:
            print(msg, self.sock)
            self.chock = True
            self.peer_radio.on_next({'id': 'msg', 'payload': msg})

        elif msg.id == Message.UNCHOCK:
            self.chock = False
            self.peer_radio.on_next({'id': 'msg', 'payload': msg})

        elif msg.id == Message.BITFIELD:
            self.peer_radio.on_next({'id': 'msg', 'payload': msg})

        elif msg.id == Message.HAVE:
            self.peer_radio.on_next({'id': 'msg', 'payload': msg})

        elif msg.id == Message.PIECE:
            # print('piece', msg.index, msg.begin, len(msg.block))
            self.peer_radio.on_next({'id': 'msg', 'payload': msg})
        else:
            print(msg, self.sock)

    def is_connected(self):
        return self.connected

    def connect(self, peer_ip, peer_port):
        if self.connected:
            return False

        handshake = Handshake.get_bytes(self.metainfo.info_hash, self.client_id)
        if handshake is None:
            self.on_disconnected()
            return False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(PeerRadioActor.SOCKET_TIMEOUT)
            self.sock.connect((peer_ip, peer_port))
            self.sock.send(handshake)

            received = self.sock.recv(Handshake.TOTAL_LEN)
            msg = Handshake.create(received)
            if msg is None or msg.info_hash != self.metainfo.info_hash:
                self.on_disconnected()
                return False

            self.sock.send(Interested.get_bytes())

        except:
            self.on_disconnected()
            return False

        self.connected = True

        self.recv_main_thread = Thread(target=PeerRadioActor.recv_main, args=(self,))
        self.recv_main_thread.daemon = True
        self.recv_main_thread.start()

        def report_keep_alive(_):
            self.actor_ref.tell({'func': 'keep_alive', 'args': None})

        self.keep_alive_subscription = Observable.interval(
            PeerRadioActor.KEEP_ALIVE_TIMEOUT * 1000).subscribe(report_keep_alive)

        self.peer_radio.on_next({'id': 'connected', 'payload': None})

        return True

    def disconnect(self):
        if not self.connected:
            return False

        self.connected = False
        self.recv_main_thread.join(PeerRadioActor.SOCKET_TIMEOUT * 2)
        self.cleanup()
        self.peer_radio.on_next({'id': 'disconnected', 'payload': None})

        return True

    def keep_alive(self):
        self.send(KeepAlive.get_bytes())

    def request(self, index, begin, length):
        if not self.chock and 0 < length <= PeerRadioActor.BLOCK_SIZE:
            # print('request', index, begin, length)
            return self.send(Request.get_bytes(index, begin, length))
        else:
            return False

    def have(self, index):
        self.send(Have.get_bytes(index))


class PeerRadio(Subject):

    @staticmethod
    def start(client_id: bytes, metainfo: MetaInfo):
        return PeerRadio(client_id, metainfo)

    def __init__(self, client_id: bytes, metainfo: MetaInfo):
        super(PeerRadio, self).__init__()
        self.actor = PeerRadioActor.start(self, client_id, metainfo)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive():
            self.actor.tell({'func': 'stop', 'args': None})

    def is_connected(self):
        return self.actor.ask({'func': 'is_connected', 'args': None})

    def connect(self, peer_ip, peer_port):
        return self.actor.ask({'func': 'connect', 'args': (peer_ip, peer_port)})

    def disconnect(self):
        return self.actor.ask({'func': 'disconnect', 'args': None})

    def request(self, index, begin, length):
        return self.actor.ask({'func': 'request', 'args': (index, begin, length)})

    def have(self, index):
        return self.actor.ask({'func': 'have', 'args': (index, )})

import socket
import logging

from threading import Thread

from TorrentPython.MetaInfo import *
from TorrentPython.PeerMessage import *
from rx import *


class PeerService(object):

    KEEP_ALIVE_TIMEOUT = 20
    BLOCK_SIZE = 2 ** 14

    def __init__(self, metainfo: MetaInfo, peer_id):
        self.metainfo = metainfo
        self.peer_id = peer_id
        self.sock = None
        self.keepAliveSubscription = None
        self.th = None
        self.remain = b''
        self.chock = True
        self.bitfield = None

    def __del__(self):
        self.cleanUp()

    def cleanUp(self):
        if self.sock is not None:
            self.sock.close()

        if self.keepAliveSubscription is not None:
            self.keepAliveSubscription.unsubscribe()

    def handShake(self, peer_ip, peer_port):
        self.cleanUp()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((peer_ip, peer_port))
        except:
            self.cleanUp()
            return False

        buf = Handshake.getBytes(self.metainfo.info_hash, self.peer_id)
        if buf is None:
            self.cleanUp()
            return False

        logging.debug(buf)

        self.sock.send(buf)
        received = self.sock.recv(Handshake.MESSAGE_LEN)

        msg = Handshake.create(received)
        if msg is None or msg.info_hash != self.metainfo.info_hash:
            self.cleanUp()
            return False

        self.keepAliveSubscription = Observable.interval(
            PeerService.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keepAlive())

        self.th = Thread(target=PeerService.messageThread, args=(self,))
        self.th.daemon = True
        self.th.start()

        return True

    def keepAlive(self):
        self.sock.send(KeepAlive.getBytes())

    def request(self, idx):
        if self.chock is True or self.bitfield is None:
            return False

        self.sock.send(Request.getBytes(idx))

    def requestAsync(self, idx, callback):
        pass

    def handle(self, buf):
        buf = self.remain + buf
        while True:
            msg, buf = Message.parse(buf)
            if msg is None:
                break
            else:
                print('Received : ', msg)
                msg.update(self)

        self.remain = buf

    def recv(self, bufsize):
        return self.sock.recv(bufsize)

    @staticmethod
    def messageThread(peerService):
        try:
            while True:
                peerService.handle(peerService.recv(PeerService.BLOCK_SIZE))
        except:
            pass

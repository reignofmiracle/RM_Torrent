import socket

from TorrentPython.TorrentUtils import *
from TorrentPython.PeerProtocol import *

from rx import *


class PeerService(object):

    KEEP_ALIVE_TIMEOUT = 5  # sec

    @staticmethod
    def create(peerInfo, info_hash: bytes):
        ret = PeerService()

        ret.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ret.sock.connect(peerInfo)
        except:
            del ret
            return None

        ret.info_hash = info_hash

        return ret

    def __init__(self):
        self.my_id = TorrentUtils.getPeerID()
        self.info_hash = None
        self.sock = None
        self.isHandShaked = False

    def __del__(self):
        if self.sock is not None:
            self.sock.close()

    def handShake(self):
        if self.isHandShaked is True:
            return True

        msg = PeerProtocol.getHandShakeMsg(self.info_hash, self.my_id)
        if msg is None:
            return False

        ret = self.sock.send(msg)
        if ret is False:
            return False

        # response = PeerProtocol.parseHandShake(self.recv(256))
        # if handShake is None or handShake[b'info_hash'] != self.info_hash:
        #     return False

        # Observable.interval(PeerService.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keepAlive())

        self.isHandShaked = True
        return True

    def keepAlive(self):
        self.sock.send(PeerProtocol.getKeepAliveMsg())

    def choke(self):
        self.sock.send(PeerProtocol.getChoke())

    def unchoke(self):
        self.sock.send(PeerProtocol.getUnchoke())

    def interested(self):
        self.sock.send(PeerProtocol.getInterested())

    def notInterest(self):
        self.sock.send(PeerProtocol.getNotInterested())

    def have(self, index):
        self.sock.send(PeerProtocol.getHave(index))

    def request(self, index, begin, length):
        self.sock.send(PeerProtocol.getRequestMsg(index, begin, length))

    def bitfield(self):
        self.sock.send(PeerProtocol.getBitfield(b' ' * 41))

    def recv(self, length):
        return self.sock.recv(length)

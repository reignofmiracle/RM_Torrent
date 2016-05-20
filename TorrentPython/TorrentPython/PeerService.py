import socket

from TorrentPython.TorrentUtils import *
from TorrentPython.PeerProtocol import *

from tornado.ioloop import PeriodicCallback


class PeerService(object):

    SOCKET_TIMEOUT = 3  # sec
    KEEP_ALIVE_TIMEOUT = 120  # sec

    def __init__(self, peerInfo, info_hash: bytes):
        self.my_id = TorrentUtils.getPeerID()
        self.info_hash = info_hash
        self.peerInfo = peerInfo
        self.sock = None
        self.isHandShaked = False
        self.keepAliveCallback = None

    def __del__(self):
        if self.sock is not None:
            self.sock.close()

    def handShake(self):
        if self.isHandShaked is True:
            return True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(PeerService.SOCKET_TIMEOUT)

        try:
            self.sock.connect(self.peerInfo)
        except:
            return False

        msg = PeerProtocol.getHandShakeMsg(self.info_hash)
        if msg is None:
            return False

        ret = self.sock.send(msg)
        if ret is False:
            return False

        handShake = PeerProtocol.parseHandShake(self.recv(128))
        if handShake is None or handShake[b'info_hash'] != self.info_hash:
            return False

        self.keepAliveCallback = PeriodicCallback(lambda: self.keepAlive(), PeerService.KEEP_ALIVE_TIMEOUT * 1000)
        self.keepAliveCallback.start()

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
        try:
            return self.sock.recv(length)
        except:
            return b''

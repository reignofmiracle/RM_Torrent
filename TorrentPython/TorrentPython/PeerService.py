import socket

from TorrentPython.TorrentUtils import *
from TorrentPython.PeerProtocol import *


class PeerService(object):

    SOCKET_TIMEOUT = 5  # sec

    def __init__(self, peerInfo, info_hash: bytes):
        self.my_id = TorrentUtils.getPeerID()
        self.info_hash = info_hash
        self.peerInfo = peerInfo
        self.sock = None
        self.handShaked = False

    def __del__(self):
        if self.sock is not None:
            self.sock.close()

    def handShake(self):
        if self.handShaked is True:
            return True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(PeerService.SOCKET_TIMEOUT)

        try:
            self.sock.connect(self.peerInfo)
        except socket.ConnectionRefusedError:
            return None

        msg = PeerProtocol.getHandShakeMsg(self.my_id, self.info_hash)
        if msg is None:
            return False

        ret = PeerService.sendMsg(self.sock, msg)
        if ret is True:
            self.handShaked = True

        return ret

    def keepAlive(self):
        msg = PeerProtocol.getKeepAliveMsg()
        return PeerService.sendMsg(self.sock, msg)

    def request(self, index, begin, length):
        msg = PeerProtocol.getRequestMsg(index, begin, length)
        return PeerService.sendMsg(self.sock, msg)

    def recv(self, length):
        return PeerService.recvMsg(self.sock, length)

    @staticmethod
    def sendMsg(sock: socket.socket, msg: bytes):
        try:
            sock.send(msg)
        except socket.timeout:
            return False
        return True

    @staticmethod
    def recvMsg(sock: socket.socket, length):
        try:
            return sock.recv(length)
        except socket.timeout:
            return b''




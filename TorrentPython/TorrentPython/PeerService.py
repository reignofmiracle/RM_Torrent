import socket

from TorrentPython.TorrentUtils import *
from TorrentPython.PeerProtocol import *


class PeerService(object):

    @staticmethod
    def create(peer, info_hash: bytes):
        if len(info_hash) != 20:
            return None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(peer)
        except socket.ConnectionRefusedError:
            return None

        obj = PeerService()
        obj.sock = sock
        obj.info_hash = info_hash

    def __init__(self):
        self.sock = None
        self.peer_id = TorrentUtils.getPeerID()
        self.info_hash = None
        pass

    def __del__(self):
        self.sock.close()

    @staticmethod
    def handShake(sock: socket.socket, peer_id: bytes, hash_info: bytes):
        msg = PeerProtocol.getHandShake(peer_id, hash_info)
        if msg is None:
            return False

        sock.send(msg)

        return True

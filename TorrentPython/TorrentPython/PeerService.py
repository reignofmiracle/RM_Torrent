import socket
import logging

from threading import Thread

from TorrentPython.PeerProtocol import *
from rx import *


class PeerService(object):

    KEEP_ALIVE_TIMEOUT = 20
    BLOCK_SIZE = 2 ^ 14

    def __init__(self, info_hash, peer_id):
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.sock = None
        self.keepAliveSubscription = None

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

        msg = PeerProtocol.getHandShakeMsg(self.info_hash, self.peer_id)
        if msg is None:
            self.cleanUp()
            return False

        logging.debug(msg)

        self.sock.send(msg)
        received = self.sock.recv(68)

        if not PeerProtocol.isHandShake(received):
            self.cleanUp()
            return False

        response = PeerProtocol.parseHandShake(received)
        if response is None or response[b'info_hash'] != self.info_hash:
            self.cleanUp()
            return False

        self.keepAliveSubscription = Observable.interval(
            PeerService.KEEP_ALIVE_TIMEOUT * 1000).subscribe(lambda t: self.keepAlive())

        self.th = Thread(target=PeerService.updateThread, args=(self,))
        self.th.start()

        return True

    def keepAlive(self):
        self.sock.send(PeerProtocol.getKeepAliveMsg())

    def update(self, msg):

        print(msg)
        if PeerProtocol.isKeepAlive(msg):
            print('KeepAlive')

    def recv(self, bufsize):
        return self.sock.recv(bufsize)

    @staticmethod
    def updateThread(peerService):
        try:
            while True:
                peerService.update(peerService.recv(PeerService.BLOCK_SIZE))
        except:
            pass

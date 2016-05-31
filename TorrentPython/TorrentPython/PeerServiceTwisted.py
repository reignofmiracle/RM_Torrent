from twisted.internet import protocol, reactor

import logging

from TorrentPython.TorrentUtils import *
from TorrentPython.PeerProtocol import *

from rx import *


class PeerServiceProtocol(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        msg = PeerProtocol.getHandShakeMsg(self.factory.peer_id, self.factory.info_hash)
        print('send handshake : ', msg, len(msg))
        # self.transport.write(msg)

    def dataReceived(self, data):
        print("data received : ", data)


class PeerServiceProtocolFactory(protocol.ClientFactory):

    def __init__(self, peer_id,  info_hash):
        self.peer_id = peer_id
        self.info_hash = info_hash

    def buildProtocol(self, addr):
        return PeerServiceProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        print('connection failed:', reason.getErrorMessage())
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
        reactor.stop()


class PeerService(object):

    def __init__(self, peer_ip, peer_port, info_hash):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.info_hash = info_hash
        self.peer_id = TorrentUtils.getPeerID()
        self.factory = PeerServiceProtocolFactory(self.peer_id, self.info_hash)

    def run(self):
        reactor.connectTCP(self.peer_ip, self.peer_port, self.factory)
        reactor.run()
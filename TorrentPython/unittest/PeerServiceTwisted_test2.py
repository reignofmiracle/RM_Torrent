from twisted.internet import reactor, protocol

HAND_SHAKE = b'\x13BitTorrent protocol\x00\x00\x00\x00\x00\x01\x00\x05i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH?\xadg\xac\x83\xd0d\x82\x8b\xa9\x07Y\x8dX\xf2\xe5"\x04!R'

TRANSMISSION_PORT = 51413


class EchoClient(protocol.Protocol):

    def connectionMade(self):
        print("Connection made.")
        self.transport.write(HAND_SHAKE[:48])

    def dataReceived(self, data):
        print("Server said:", data)


class EchoFactory(protocol.ClientFactory):

    def buildProtocol(self, addr):
        return EchoClient()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed.")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost.")
        reactor.stop()


reactor.connectTCP('127.0.0.1', TRANSMISSION_PORT, EchoFactory())
reactor.run()
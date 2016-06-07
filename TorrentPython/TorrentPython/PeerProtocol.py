import struct
from enum import Enum


class PeerProtocol(object):

    PROTOCOL_ID = b'BitTorrent protocol'

    class MessageID(Enum):
        CHOCK = 0
        UNCHOCK = 1
        INTERESTED = 2
        NOT_INTERESTED = 3
        HAVE = 4
        BITFIELD = 5
        REQUEST = 6

    @staticmethod
    def getHandShakeMsg(info_hash: bytes, peer_id: bytes):
        if len(info_hash) != 20 or len(peer_id) != 20:
            return None

        pstrlen = struct.pack('!B', len(PeerProtocol.PROTOCOL_ID))
        pstr = PeerProtocol.PROTOCOL_ID
        reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'

        return pstrlen + pstr + reserved + info_hash + peer_id

    @staticmethod
    def getKeepAliveMsg():
        lengthPrefix = struct.pack('!I', 0)
        print(lengthPrefix)
        return lengthPrefix

    @staticmethod
    def getChoke():
        lengthPrefix = struct.pack('!I', 1)
        msgID = struct.pack('!B', PeerProtocol.MessageID.CHOCK.value)
        return lengthPrefix + msgID

    @staticmethod
    def getUnchoke():
        lengthPrefix = struct.pack('!I', 1)
        msgID = struct.pack('!B', PeerProtocol.MessageID.UNCHOCK.value)
        return lengthPrefix + msgID

    @staticmethod
    def getInterested():
        lengthPrefix = struct.pack('!I', 1)
        msgID = struct.pack('!B', PeerProtocol.MessageID.INTERESTED.value)
        return lengthPrefix + msgID

    @staticmethod
    def getNotInterested():
        lengthPrefix = struct.pack('!I', 1)
        msgID = struct.pack('!B', PeerProtocol.MessageID.NOT_INTERESTED.value)
        return lengthPrefix + msgID

    @staticmethod
    def getHave(index):
        lengthPrefix = struct.pack('!I', 1)
        msgID = struct.pack('!B', PeerProtocol.MessageID.HAVE.value)
        pieceIndexPayload = struct.pack('!I', index)
        return lengthPrefix + msgID + pieceIndexPayload

    @staticmethod
    def getBitfield(bitfield: bytes):
        lengthPrefix = struct.pack('!I', 1 + len(bitfield))
        msgID = struct.pack('!B', PeerProtocol.MessageID.BITFIELD.value)
        return lengthPrefix + msgID + bitfield

    @staticmethod
    def getRequestMsg(index, begin, length):
        lengthPrefix = struct.pack('!I', 13)
        msgID = struct.pack('!B', PeerProtocol.MessageID.REQUEST.value)
        indexPayload = struct.pack('!I', index)
        beginPayload = struct.pack('!I', begin)
        lengthPayload = struct.pack('!I', length)
        return lengthPrefix + msgID + indexPayload + beginPayload + lengthPayload

    @staticmethod
    def parseHandShake(msg):
        return {b'pstrlen': msg[0:0 + 1],
                b'pstr': msg[1:1 + 19],
                b'reserved': msg[20:20 + 8],
                b'info_hash': msg[28:28 + 20],
                b'peer_id': msg[48:48 + 20]}

    @staticmethod
    def isHandShake(msg):
        if len(msg) is not 68:
            return False

        handshake = PeerProtocol.parseHandShake(msg)

        if struct.unpack('>B', handshake[b'pstrlen'])[0] != len(PeerProtocol.PROTOCOL_ID):
            return False

        if handshake[b'pstr'] != PeerProtocol.PROTOCOL_ID:
            return False

        return True

    @staticmethod
    def isKeepAlive(msg):
        return b'\x00\x00\x00\x00' == msg

    @staticmethod
    def isChock(msg):
        return False

    @staticmethod
    def isUnchock(msg):
        return False

    @staticmethod
    def isInterest(msg):
        return False

    @staticmethod
    def isNotInterest(msg):
        return False

    @staticmethod
    def isHave(msg):
        return False

    @staticmethod
    def isBitfield(msg):
        return False

    @staticmethod
    def isRequest(msg):
        return False

    @staticmethod
    def isPiece(msg):
        return False

    @staticmethod
    def isCancel(msg):
        return False

    @staticmethod
    def isPort(msg):
        return False

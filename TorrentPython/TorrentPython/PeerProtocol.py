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
    def getHandShakeMsg(peer_id: bytes, info_hash: bytes):
        if len(peer_id) != 20 or len(info_hash) != 20:
            return None

        pstrlen = struct.pack('!B', len(PeerProtocol.PROTOCOL_ID))
        pstr = PeerProtocol.PROTOCOL_ID
        reserved = b'\x00' * 8

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
        if not PeerProtocol.isHandShake(msg):
            return None

        ret = {b'pstrlen': msg[0],
               b'pstr': msg[1:1 + 19],
               b'reserved': msg[20:20 + 8],
               b'info_hash': msg[28:28 + 20]}

        if len(msg) is 68:
            ret[b'peer_id'] = msg[48:68]

        return ret

    @staticmethod
    def isHandShake(msg):
        if not (len(msg) is 48 or len(msg) is 68):
            return False

        if struct.unpack('>B', msg[:1])[0] != len(PeerProtocol.PROTOCOL_ID):
            return False

        if msg[1:1 + len(PeerProtocol.PROTOCOL_ID)] != PeerProtocol.PROTOCOL_ID:
            return False

        return True

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

        pstrlen = struct.pack('B', 49 + len(PeerProtocol.PROTOCOL_ID))
        pstr = PeerProtocol.PROTOCOL_ID
        reserved = b' ' * 8

        return pstrlen + pstr + reserved + info_hash + peer_id

    @staticmethod
    def getKeepAliveMsg():
        lengthPrefix = struct.pack('>L', 0)
        return lengthPrefix

    @staticmethod
    def getRequestMsg(index, begin, length):
        lengthPrefix = struct.pack('>L', 13)
        msgID = struct.pack('>B', PeerProtocol.MessageID.REQUEST.value)
        indexPayload = struct.pack('>L', index)
        beginPayload = struct.pack('>L', begin)
        lengthPayload = struct.pack('>L', length)
        return lengthPrefix + msgID + indexPayload + beginPayload + lengthPayload



import struct


class PeerProtocol(object):

    PROTOCOL_ID = b'BitTorrent protocol'

    @staticmethod
    def getHandShakeMsg(info_hash: bytes, peer_id: bytes):
        if len(info_hash) != 20 or len(peer_id) != 20:
            return None

        pstrlen = struct.pack('B', 49 + len(PeerProtocol.PROTOCOL_ID))
        pstr = PeerProtocol.PROTOCOL_ID
        reserved = b' ' * 8

        return pstrlen + pstr + reserved + info_hash + peer_id



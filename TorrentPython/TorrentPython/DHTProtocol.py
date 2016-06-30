import socket
import struct

from TorrentPython.Bencode import *


class DHTProtocol(object):

    COMPACT_NODE_INFO_LENGTH = 26  # byte

    @staticmethod
    def get_ping(client_id: bytes):
        return Bencode.encode(
            {b't': b'aa', b'y': b'q', b'q': b'ping', b'a': {b'id': client_id}})

    @staticmethod
    def get_peers(client_id: bytes, info_hash: bytes):
        if len(info_hash) is not 20:
            return None

        return Bencode.encode(
            {b't': b'aa', b'y': b'q', b'q': b'get_peers', b'a': {b'id': client_id, b'info_hash': info_hash}})

    @staticmethod
    def is_response(response: dict):
        return b'r' in response

    @staticmethod
    def parse_peers(response: dict):
        peers = []
        nodes = {}

        if not DHTProtocol.is_response(response):
            return peers, nodes

        source = response.get(b'r').get(b'values')
        if source:
            for sample in source:
                peers.append((socket.inet_ntoa(sample[:4]), struct.unpack('!H', sample[4:4 + 2])[0]))

        source = response.get(b'r').get(b'nodes')
        if source:
            for idx in range(0, len(source), DHTProtocol.COMPACT_NODE_INFO_LENGTH):
                sample = source[idx:idx + DHTProtocol.COMPACT_NODE_INFO_LENGTH]
                nodes[sample[:20]] = (socket.inet_ntoa(sample[20:20 + 4]), struct.unpack('!H', sample[24:24 + 2])[0])

        return peers, nodes

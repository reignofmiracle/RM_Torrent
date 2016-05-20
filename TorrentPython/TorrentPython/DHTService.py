import socket
import struct

from TorrentPython.Bencode import *
from TorrentPython.TorrentUtils import *


class DHTService(object):

    TIMEOUT_SEC = 0.5
    # TIMEOUT_SEC = 15 # sec

    COMPACT_IP_PORT_INFO_LENGTH = 6  # byte
    COMPACT_NODE_INFO_LENGTH = 26  # byte

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(DHTService.TIMEOUT_SEC)
        pass

    def __del__(self):
        self.sock.close()

    def ping(self, addr):
        rid = TorrentUtils.getPeerID()
        query = {b't': b'aa', b'y': b'q', b'q': b'ping', b'a': {b'id': rid}}
        return self.request(addr, query)

    def findNode(self, addr, target):
        if len(target) is not 20:
            return None

        rid = TorrentUtils.getPeerID()
        query = {b't': b'aa', b'y': b'q', b'q': b'find_node', b'a': {b'id': rid, b'target': target}}
        return self.request(addr, query)

    def getPeers(self, addr, info_hash):
        if len(info_hash) is not 20:
            return None

        rid = TorrentUtils.getPeerID()
        query = {b't': b'aa', b'y': b'q', b'q': b'get_peers', b'a': {b'id': rid, b'info_hash': info_hash}}
        return self.request(addr, query)

    def request(self, addr, query):
        bencode = Bencode.encode(query)
        if bencode is None:
            return False

        self.sock.sendto(bencode, addr)

        try:
            recv, addr = self.sock.recvfrom(10240)
        except:
            return None

        return Bencode.decode(recv)

    @staticmethod
    def isResponseError(response: dict):
        return b'e' in response

    @staticmethod
    def isResponseNodes(response: dict):
        return b'r' in response and b'nodes' in response[b'r']

    @staticmethod
    def isResponsePeers(response: dict):
        return b'r' in response and b'values' in response[b'r']

    @staticmethod
    def parsePeers(response: dict):
        if not DHTService.isResponsePeers(response):
            return []

        source = response[b'r'][b'values']
        peers = []
        for sample in source:
            peers.append((socket.inet_ntoa(sample[:4]), struct.unpack('!H', sample[4:4 + 2])[0]))

        return peers

    @staticmethod
    def parseNodes(response: dict):
        if not DHTService.isResponseNodes(response):
            return {}

        source = response[b'r'][b'nodes']
        nodes = {}
        for idx in range(0, len(source), DHTService.COMPACT_NODE_INFO_LENGTH):
            sample = source[idx:idx + DHTService.COMPACT_NODE_INFO_LENGTH]
            nodes[sample[:20]] = (socket.inet_ntoa(sample[20:20 + 4]), struct.unpack('!H', sample[24:24 + 2])[0])

        return nodes



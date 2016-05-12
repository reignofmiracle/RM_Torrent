import random
import socket
import struct

from TorrentPython.Bencode import *

INITIAL_NODE_HOST = 'router.utorrent.com'
INITIAL_NODE_PORT = 6881
INITIAL_NODE_ADDR = (socket.gethostbyname(INITIAL_NODE_HOST), INITIAL_NODE_PORT)

TIMEOUT_SEC = 15 # sec

COMPACT_IP_PORT_INFO_LENGTH = 6  # byte
COMPACT_NODE_INFO_LENGTH = 26  # byte


class DHTService(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT_SEC)
        pass

    def __del__(self):
        self.sock.close()

    def ping(self, addr):
        rid = DHTService.getID()
        query = {b't': b'aa', b'y': b'q', b'q': b'ping', b'a': {b'id': rid}}
        return self.request(addr, query)

    def findNode(self, addr, target):
        rid = DHTService.getID()
        query = {b't': b'aa', b'y': b'q', b'q': b'find_node', b'a': {b'id': rid, b'target': target}}
        return self.request(addr, query)

    def getPeers(self, addr, info_hash):
        if len(info_hash) is not 20:
            return None

        rid = DHTService.getID()
        query = {b't': b'aa', b'y': b'q', b'q': b'get_peers', b'a': {b'id': rid, b'info_hash': info_hash}}
        return self.request(addr, query)

    def request(self, addr, query):
        bencode = Bencode.encode(query)
        if bencode is None:
            return False

        self.sock.sendto(bencode, addr)

        try:
            recv, addr = self.sock.recvfrom(10240)
        except socket.timeout:
            return None

        return Bencode.decode(recv)

    @staticmethod
    def getID():
        return bytes(random.randint(0, 255) for _ in range(20))

    @staticmethod
    def isResponseError(response):
        if type(response) is not dict:
            return False

        return b'e' in response

    @staticmethod
    def isResponseNodes(response):
        if type(response) is not dict:
            return False

        return b'r' in response and b'nodes' in response[b'r']

    @staticmethod
    def isResponsePeers(response):
        if type(response) is not dict:
            return False

        return b'r' in response and b'values' in response[b'r']

    @staticmethod
    def parsePeers(response):
        if not DHTService.isResponsePeers(response):
            return None

        source = response[b'r'][b'values']
        if len(source) % COMPACT_IP_PORT_INFO_LENGTH is not 0:
            print("Peers error.")
            return None

        peers = []
        for idx in range(0, len(source), COMPACT_IP_PORT_INFO_LENGTH):
            sample = source[idx:idx + COMPACT_IP_PORT_INFO_LENGTH]
            peers.append((sample[:4], sample[4:4 + 2]))

        return peers

    @staticmethod
    def parseNodes(response):
        if not DHTService.isResponseNodes(response):
            return None

        source = response[b'r'][b'nodes']
        if len(source) % COMPACT_NODE_INFO_LENGTH is not 0:
            print("Nodes error.")
            return None

        nodes = []
        for idx in range(0, len(source), COMPACT_NODE_INFO_LENGTH):
            sample = source[idx:idx + COMPACT_NODE_INFO_LENGTH]
            nodes.append((sample[:20], socket.inet_ntoa(sample[20:20 + 4]), struct.unpack('>H', sample[24:24 + 2])[0]))

        return nodes



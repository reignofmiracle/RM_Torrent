import time
import socket

from TorrentPython.DHTProtocol import *


class DHTExplorer(object):

    TIMEOUT_SEC = 1
    NODE_EXPANSION_SIZE = 7

    @staticmethod
    def get_peerout(peer_limit):
        return (lambda a: False) if peer_limit <= 0 else (lambda b: b >= peer_limit)

    @staticmethod
    def get_timeout(time_limit):
        start_time = time.clock()
        return (lambda: False) if time_limit <= 0 else (lambda: time.clock() - start_time > time_limit)

    @staticmethod
    def update_routing_table(routing_table: dict, working_table: dict, info_hash: bytes):
        updated_routing_table = dict(routing_table)

        if len(working_table) == 0:
            return updated_routing_table

        intersect = [key for key in working_table if key in updated_routing_table]
        for key in intersect:
            del working_table[key]

        for index, key in enumerate(sorted(working_table, key=lambda v: bytes((a ^ b) for a, b in zip(info_hash, v)))):
            updated_routing_table[key] = working_table[key]
            if index >= DHTExplorer.NODE_EXPANSION_SIZE:
                break

        return updated_routing_table

    def __init__(self, client_id: bytes, routing_table: dict):
        self.client_id = client_id
        self.routing_table = routing_table

        self.found_peers = set()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(DHTExplorer.TIMEOUT_SEC)

    def __del__(self):
        self.sock.close()

    def explore(self, info_hash: bytes, peer_limit, time_limit):
        peerout = DHTExplorer.get_peerout(peer_limit)
        timeout = DHTExplorer.get_timeout(time_limit)

        updated_routing_table = dict(self.routing_table)
        working_table = dict(self.routing_table)

        peer_list = set()
        while len(working_table) > 0 and not peerout(len(peer_list)) and not timeout():
            p, working_table = self.find_peers(info_hash, working_table, peerout, timeout)
            peer_list |= p - self.found_peers

            updated_routing_table = DHTExplorer.update_routing_table(
                updated_routing_table, working_table, info_hash)

        self.routing_table = updated_routing_table

        self.found_peers |= peer_list
        return list(peer_list)

    def find_peers(self, info_hash: bytes, routing_table: dict, peerout, timeout):
        peer_list = set()
        updated_routing_table = {}

        if len(routing_table) == 0:
            return peer_list, updated_routing_table

        for k in sorted(routing_table, key=lambda v: bytes((a ^ b) for a, b in zip(info_hash, v))):
            p, r = self.get_peers(info_hash, *routing_table[k])

            updated_routing_table.update(r)
            peer_list = peer_list.union(p)

            if peerout(len(peer_list)) or timeout():
                break

        return peer_list, updated_routing_table

    def get_peers(self, info_hash: bytes, node_ip, node_port):
        try:
            self.sock.sendto(DHTProtocol.get_peers(self.client_id, info_hash), (node_ip, node_port))
            return DHTProtocol.parse_peers(Bencode.decode(self.sock.recv(1024)))
        except:
            return [], {}

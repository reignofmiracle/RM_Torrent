import socket
import urllib.parse
import struct


class TrackerProtocol(object):

    class Settings(object):
        COMPACT = 1
        NO_PEER_ID = None
        EVENT = None
        IP = None
        NUM_WANT = None
        KEY = None
        TRACKER_ID = None

    @staticmethod
    def get_request(client_id, info_hash):
        payload = dict()
        payload['info_hash'] = urllib.parse.quote(info_hash, safe='%')
        payload['peer_id'] = urllib.parse.quote(client_id, safe='%')
        payload['uploaded'] = 0
        payload['downloaded'] = 0
        payload['left'] = 100
        payload['event'] = 'started'
        payload['compact'] = 1

        return '?' + urllib.parse.urlencode(payload, encoding='utf-8', safe='%')

    @staticmethod
    def parse_peers(response: dict):  # decoded
        if response.get(b'failure reason'):
            return []

        peers = response.get(b'peers')
        if peers is None or len(peers) % 6 is not 0:
            return []

        return [(socket.inet_ntoa(peers[i:i+4]), struct.unpack('!H', peers[i+4:i+4+2])[0])
                for i in range(0, len(peers), 6)]

import urllib.request
import time

from TorrentPython.Bencode import Bencode
from TorrentPython.TrackerProtocol import *


class TrackerService(object):

    @staticmethod
    def request(url, client_id, info_hash):
        params = TrackerProtocol.get_request(client_id, info_hash)
        request = urllib.request.Request(url + params, method='GET')
        try:
            return urllib.request.urlopen(request).read()
        except:
            return None

    @staticmethod
    def is_waiting_time(response, request_time):
        current_time = time.clock()
        interval = response.get(b'interval')
        return interval < current_time - request_time

    def __init__(self, client_id, metainfo):
        self.client_id = client_id
        self.metainfo = metainfo

        self.found_peers = set()

        tmp_announce_list = set()
        tmp_announce_list.add(self.metainfo.get_announce())
        if self.metainfo.get_announce_list():
            for announce_list in self.metainfo.get_announce_list():
                for announce in announce_list:
                    tmp_announce_list.add(announce)

        self.announce_list = list(tmp_announce_list)

        self.announce_response_list = dict()  # (response, request_time)
        self.announce_pos = 0

    def get_peers(self):
        announce = self.announce_list[self.announce_pos].decode()
        announce_response = self.announce_response_list.get(announce)

        self.announce_pos += 1
        if self.announce_pos >= len(self.announce_list):
            self.announce_pos = 0

        if announce_response is None or TrackerService.is_waiting_timea(*announce_response) is False:
            response = TrackerService.request(announce, self.client_id, self.metainfo.info_hash)
            if response:
                peer_list = []
                for peer in TrackerProtocol.parse_peers(Bencode.decode(response)):
                    if peer not in self.found_peers:
                        peer_list.append(peer)
                        self.found_peers.add(peer)
                return peer_list

        return []

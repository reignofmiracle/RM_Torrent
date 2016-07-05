import pykka

from TorrentPython.DHTExplorer import *
from TorrentPython.MetaInfo import MetaInfo
from TorrentPython.TrackerService import TrackerService


class PeerProviderActor(pykka.ThreadingActor):

    def __init__(self, client_id: bytes, metainfo: MetaInfo, routing_table: dict):
        super(PeerProviderActor, self).__init__()
        self.explorer = DHTExplorer(client_id, metainfo.info_hash, routing_table)
        self.tracker_service = TrackerService(client_id, metainfo)
        self.metainfo = metainfo

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def set_expedition_timeout(self, expedition_timeout):
        self.explorer.set_expedition_timeout(expedition_timeout)

    def get_routing_table(self):
        return self.explorer.routing_table

    def get_peers(self, peer_size):
        # peers = self.tracker_service.get_peers(peer_size)
        # if len(peers) > 0:
        #     return peers
        #
        # return self.explorer.explore(peer_size)
        # time.sleep(3)
        # return [('192.168.10.12', 51413), ('192.168.10.2', 51413), ('192.168.10.4', 51413)]
        # return [('192.168.10.12', 51413), ('192.168.10.2', 51413)]

        # return [('39.112.128.233', 51413),
        #         ('218.236.104.230', 55111),
        #         ('178.32.59.188', 57551),
        #         ('109.229.161.139', 15737),
        #         ('80.190.128.61', 6881),
        #         ('124.64.202.135', 13176),
        #         ('109.229.161.139', 15737)]

        return [('39.110.51.141', 6881)]


class PeerProvider(object):

    @staticmethod
    def start(client_id: bytes, metainfo: MetaInfo, routing_table: dict):
        return PeerProvider(client_id, metainfo, routing_table)

    def __init__(self, client_id: bytes, metainfo: MetaInfo, routing_table: dict):
        self.actor = PeerProviderActor.start(client_id, metainfo, routing_table)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive():
            self.actor.stop()

    def set_expedition_timeout(self, expedition_timeout):
        return self.actor.ask({'func': 'set_expedition_timeout', 'args': (expedition_timeout, )})

    def get_routing_table(self):
        return self.actor.ask({'func': 'get_routing_table', 'args': None})

    def get_peers(self, peer_size=None):
        return self.actor.ask({'func': 'get_peers', 'args': (peer_size, )})

import pykka

from TorrentPython.DHTExplorer import *


class PeerDetectiveActor(pykka.ThreadingActor):

    def __init__(self, client_id: bytes, routing_table: dict):
        super(PeerDetectiveActor, self).__init__()
        self.explorer = DHTExplorer(client_id, routing_table)

    def on_receive(self, message):
        return message.get('func')(self)

    def find_peers(self, info_hash: bytes, peer_limit, time_limit):
        return self.explorer.explore(info_hash, peer_limit, time_limit)

    def get_routing_table(self):
        return self.explorer.routing_table


class PeerDetective(object):

    def __init__(self, client_id: bytes, routing_table: dict):
        self.actor = PeerDetectiveActor.start(client_id, routing_table)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def find_peers(self, info_hash: bytes, peer_limit=None, time_limit=None):
        return self.actor.ask({'func': lambda x: x.find_peers(info_hash, peer_limit, time_limit)})

    def get_routing_table(self):
        return self.actor.ask({'func': lambda x: x.get_routing_table()})

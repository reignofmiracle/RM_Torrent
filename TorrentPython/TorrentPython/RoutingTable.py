class RoutingTable(object):
    UTORRENT_NODE_ID = b'\xeb\xff6isQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
    UTORRENT_NODE_IP = '82.221.103.244'  # 'router.utorrent.com',
    UTORRENT_NODE_PORT = 6881
    UTORRENT_NODE_ADDR = (UTORRENT_NODE_IP, UTORRENT_NODE_PORT)

    BITTORRENT_NODE_ID = b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
    BITTORRENT_NODE_IP = '67.215.246.10'  # 'router.bittorrent.com'
    BITTORRENT_NODE_PORT = 6881
    BITTORRENT_NODE_ADDR = (BITTORRENT_NODE_IP, BITTORRENT_NODE_PORT)

    TRANSMISSION_NODE_ID = b'\x8d\xb1S*D+\xb3\xf8\xc4b\xd7\xeb\x1c\xad%\xdeXC\xe5\xd8'
    TRANSMISSION_NODE_IP = '91.121.59.153'  # 'dht.transmissionbt.com'
    TRANSMISSION_NODE_PORT = 6881
    TRANSMISSION_NODE_ADDR = (TRANSMISSION_NODE_IP, TRANSMISSION_NODE_PORT)

    INITIAL_ROUTING_TABLE = {UTORRENT_NODE_ID: UTORRENT_NODE_ADDR,
                             BITTORRENT_NODE_ID: BITTORRENT_NODE_ADDR,
                             TRANSMISSION_NODE_ID: TRANSMISSION_NODE_ADDR}

    @staticmethod
    def save(routing_table: dict, path):
        with open(path, 'wb') as f:
            f.write(str(routing_table).encode())

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return eval(f.read())

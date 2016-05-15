import random


class TorrentUtils(object):

    @staticmethod
    def getPeerID():
        return bytes(random.randint(0, 255) for _ in range(20))

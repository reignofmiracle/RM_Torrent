import os


class TorrentUtils(object):

    @staticmethod
    def getPeerID():
        return os.urandom(20)

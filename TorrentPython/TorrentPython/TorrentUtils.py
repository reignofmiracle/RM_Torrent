import os

from TorrentPython.Defines import *


class TorrentUtils(object):

    @staticmethod
    def getPeerID():
        client = b'-' + RM_CLIENT_ID + RM_CLIENT_VERSION + b'-'
        return client + os.urandom(20 - len(client))

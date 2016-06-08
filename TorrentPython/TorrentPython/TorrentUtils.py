import os

from TorrentPython.Defines import *


class TorrentUtils(object):

    @staticmethod
    def getPeerID():
        client = b'-' + Defines.RM_CLIENT_ID + Defines.RM_CLIENT_VERSION + b'-'
        return client + os.urandom(20 - len(client))

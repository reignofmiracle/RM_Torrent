import os


class TorrentUtils(object):

    @staticmethod
    def getPeerID():
        clientID = b'-RM0101-'
        return clientID + os.urandom(20 - len(clientID))

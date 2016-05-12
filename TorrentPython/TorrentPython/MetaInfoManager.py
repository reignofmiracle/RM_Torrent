import os
import hashlib

from TorrentPython.Bencode import *


class MetaInfoManager(object):

    @staticmethod
    def parseFromMagnet(magnetStr):
        metaInfo = {}
        return metaInfo, b''  # TODO:

    @staticmethod
    def parseFromTorrent(torrentPath):
        if torrentPath is None:
            return None

        if not os.path.exists(torrentPath):
            return None

        with open(torrentPath, 'rb') as f:
            source = f.read()

        if source is None:
            return None
        
        return Bencode.decode(source)

    @staticmethod
    def getInfoHashFromTorrent(torrentPath):
        if torrentPath is None:
            return None

        if not os.path.exists(torrentPath):
            return None

        with open(torrentPath, 'rb') as f:
            source = f.read()

        if source is None:
            return None

        bencoded_info = Bencode.getBencode_Info(source)
        if bencoded_info is None:
            return None

        return hashlib.sha1(bencoded_info).digest()
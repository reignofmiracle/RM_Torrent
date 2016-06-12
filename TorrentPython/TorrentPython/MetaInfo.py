import os
import hashlib

from TorrentPython.Bencode import *


class MetaInfo(object):

    @staticmethod
    def parseMagnet(magnetStr):
        metaInfo = {}
        return metaInfo, b''  # TODO:

    @staticmethod
    def parseTorrent(torrentPath):
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

    @staticmethod
    def createFromTorrent(torrentPath):
        metainfo = MetaInfo.parseTorrent(torrentPath)
        if metainfo is None:
            return None

        info_hash = MetaInfo.getInfoHashFromTorrent(torrentPath)
        if info_hash is None:
            return None

        return MetaInfo(metainfo, info_hash)

    def __init__(self, metainfo, info_hash):
        self.metainfo = metainfo
        self.info_hash = info_hash

    def getInfoPieceLength(self):
        return self.metainfo[b'info'][b'piece length']

    def getInfoLength(self):
        return self.metainfo[b'info'][b'length']

    def getInfoPieceNum(self):
        pieceNum = int(self.getInfoLength() / self.getInfoPieceLength())

        if (self.getInfoLength() % self.getInfoPieceLength()) is not 0:
            pieceNum += 1

        return pieceNum

    def isValidPieceIndex(self, index):
        return 0 <= index < self.getInfoPieceNum()

    def isLastPieceIndex(self, index):
        return index == (self.getInfoPieceNum() - 1)

    def getLastPieceLength(self):
        remain = self.getInfoLength() % self.getInfoPieceLength()
        return remain if remain > 0 else self.getInfoPieceLength()

    def getPieceLength(self, index):
        return self.getLastPieceLength() if self.isLastPieceIndex(index) else self.getInfoPieceLength()



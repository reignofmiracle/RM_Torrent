from abc import abstractmethod
import os
import hashlib
from enum import *

from TorrentPython.Bencode import *


class MetaInfo(object):

    @staticmethod
    def parseMagnet(magnetStr):
        metaInfo = {}
        return metaInfo, b''  # TODO:

    @staticmethod
    def parseTorrent(torrentPath):
        if not os.path.exists(torrentPath):
            return None

        with open(torrentPath, 'rb') as f:
            source = f.read()

        return Bencode.decode(source)

    @staticmethod
    def getInfoHashFromTorrent(torrentPath):
        if not os.path.exists(torrentPath):
            return None

        with open(torrentPath, 'rb') as f:
            source = f.read()

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

    def getInfo(self):
        return BaseInfo.create(self.metainfo.get(b'info'))

    def getAnnounce(self):
        return self.metainfo.get(b'announce')

    def getAnnounceList(self):
        return self.metainfo.get(b'announce-list')

    def getCreationDate(self):
        return self.metainfo.get(b'creation date')

    def getComment(self):
        return self.metainfo.get(b'comment')

    def getCreatedBy(self):
        return self.metainfo.get(b'created by')

    def getEncoding(self):
        return self.metainfo.get(b'encoding')

    def getFileMode(self):
        return BaseInfo.getFileMode(self.metainfo.get(b'info'))


class BaseInfo(object):

    @unique
    class FILE_MODE(Enum):
        SINGLE = 1
        MULTI = 2

    @staticmethod
    def getFileMode(info: dict):
        if info.get(b'files') is None:
            return BaseInfo.FILE_MODE.SINGLE
        else:
            return BaseInfo.FILE_MODE.MULTI

    @staticmethod
    def create(info: dict):
        if BaseInfo.getFileMode(info) == BaseInfo.FILE_MODE.SINGLE:
            return SInfo.create(info)
        else:
            return MInfo.create(info)

    def __init__(self, info: dict):
        self.info = info

    def getPieceLength(self):
        return self.info.get(b'piece length')

    def getPieces(self):
        return self.info.get(b'pieces')

    @abstractmethod
    def getLength(self):
        return NotImplemented

    @abstractmethod
    def getPieceNum(self):
        return NotImplemented

    def isValidPieceIndex(self, index):
            return 0 <= index < self.getPieceNum()

    def isLastPieceIndex(self, index):
        return index == (self.getPieceNum() - 1)

    def getLastPieceLength(self):
        if self.last_piece_length is None:
            self.last_piece_length = self.getLength() - (self.getPieceNum() - 1) * self.getPieceLength()

        return self.last_piece_length

    def getPieceLength_index(self, index):
        return self.getLastPieceLength() if self.isLastPieceIndex(index) else self.getPieceLength()


class SInfo(BaseInfo):

    @staticmethod
    def create(info: dict):
        if BaseInfo.getFileMode(info) != BaseInfo.FILE_MODE.SINGLE:
            return None
        else:
            return SInfo(info)

    def __init__(self, info: dict):
        super(SInfo, self).__init__(info)
        self.file_mode = BaseInfo.FILE_MODE.SINGLE
        self.piece_num = None
        self.last_piece_length = None

    def getFileMode(self):
        return self.file_mode

    def getName(self):
        return self.info.get(b'name')

    def getLength(self):
        return self.info.get(b'length')

    def getMD5sum(self):
        return self.info.get(b'md5sum')

    def getPieceNum(self):
        if self.piece_num is None:
            self.piece_num = int(self.getLength() / self.getPieceLength())
            if self.getLength() % self.getPieceLength() is not 0:
                self.piece_num += 1

        return self.piece_num


class MInfo(BaseInfo):

    class File(object):
        def __init__(self, file):
            self.file = file

        def getLength(self):
            return self.file.get(b'length')

        def getMD5sum(self):
            return self.file.get(b'md5sum')

        def getPath(self):
            return self.file.get(b'path')

        def getFullPath(self):
            fullPath = b''
            for item in self.getPath():
                fullPath += (item + b'/')
            return fullPath[:-1]

    @staticmethod
    def create(info: dict):
        if BaseInfo.getFileMode(info) != BaseInfo.FILE_MODE.MULTI:
            return None
        else:
            return MInfo(info)

    def __init__(self, info: dict):
        super(MInfo, self).__init__(info)
        self.file_mode = BaseInfo.FILE_MODE.MULTI
        self.files = self.info.get(b'files')
        self.length = None
        self.piece_num = None
        self.last_piece_length = None

    def getFileMode(self):
        return self.file_mode

    def getName(self):
        return self.info.get(b'name')

    def getLength(self):
        if self.length is None:
            self.length = 0
            for file in self.files:
                self.length += file.get(b'length')

        return self.length

    def getFile(self, index):
        return MInfo.File(self.files[index]) if 0 <= index < len(self.files) else None

    def getFiles(self):
        for file in self.files:
            yield MInfo.File(file)

    def getPieceNum(self):
        if self.piece_num is None:
            self.piece_num = int(self.getLength() / self.getPieceLength())
            if self.getLength() % self.getPieceLength() is not 0:
                self.piece_num += 1

        return self.piece_num








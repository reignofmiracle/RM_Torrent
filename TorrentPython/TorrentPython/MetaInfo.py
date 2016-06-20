from abc import abstractmethod
import os
import hashlib
from enum import *

from TorrentPython.Bencode import *


class MetaInfo(object):

    @staticmethod
    def parse_torrent(path):
        if not os.path.exists(path):
            return None

        with open(path, 'rb') as f:
            source = f.read()

        return Bencode.decode(source)

    @staticmethod
    def get_info_hash_from_torrent(path):
        if not os.path.exists(path):
            return None

        with open(path, 'rb') as f:
            source = f.read()

        bencoded_info = Bencode.get_info_dictionary(source)
        return hashlib.sha1(bencoded_info).digest() if bencoded_info else None

    @staticmethod
    def create_from_torrent(torrentPath):
        metainfo = MetaInfo.parse_torrent(torrentPath)
        if metainfo is None:
            return None

        info_hash = MetaInfo.get_info_hash_from_torrent(torrentPath)
        if info_hash is None:
            return None

        return MetaInfo(metainfo, info_hash)

    def __init__(self, metainfo, info_hash):
        self.metainfo = metainfo
        self.info_hash = info_hash

    def get_info(self):
        return BaseInfo.create(self.metainfo.get(b'info'))

    def get_announce(self):
        return self.metainfo.get(b'announce')

    def get_announce_list(self):
        return self.metainfo.get(b'announce-list')

    def get_creation_date(self):
        return self.metainfo.get(b'creation date')

    def get_comment(self):
        return self.metainfo.get(b'comment')

    def get_created_by(self):
        return self.metainfo.get(b'created by')

    def get_encoding(self):
        return self.metainfo.get(b'encoding')

    def get_file_mode(self):
        return BaseInfo.get_file_mode(self.metainfo.get(b'info'))


class BaseInfo(object):

    @unique
    class FILE_MODE(Enum):
        SINGLE = 1
        MULTI = 2

    @staticmethod
    def get_file_mode(info: dict):
        return BaseInfo.FILE_MODE.MULTI if info.get(b'files') else BaseInfo.FILE_MODE.SINGLE

    @staticmethod
    def create(info: dict):
        return SInfo.create(info) if BaseInfo.get_file_mode(info) == BaseInfo.FILE_MODE.SINGLE else MInfo.create(info)

    def __init__(self, info: dict):
        self.info = info

    def get_piece_length(self):
        return self.info.get(b'piece length')

    def get_pieces(self):
        return self.info.get(b'pieces')

    @abstractmethod
    def get_length(self):
        return NotImplemented

    @abstractmethod
    def get_piece_num(self):
        return NotImplemented

    def is_valid(self, index):
        return 0 <= index < self.get_piece_num()

    def get_piece_length_index(self, index):
        if not self.is_valid(index):
            return 0

        if index == self.get_piece_num() - 1:
            remain = self.get_length() % self.get_piece_length()
            return remain if remain else self.get_piece_length()
        else:
            return self.get_piece_length()


class SInfo(BaseInfo):

    @staticmethod
    def create(info: dict):
        return SInfo(info) if BaseInfo.get_file_mode(info) == BaseInfo.FILE_MODE.SINGLE else None

    def __init__(self, info: dict):
        super(SInfo, self).__init__(info)
        self.file_mode = BaseInfo.FILE_MODE.SINGLE
        self.piece_num = None
        self.last_piece_length = None

    def get_file_mode(self):
        return self.file_mode

    def get_name(self):
        return self.info.get(b'name')

    def get_length(self):
        return self.info.get(b'length')

    def get_md5sum(self):
        return self.info.get(b'md5sum')

    def get_piece_num(self):
        if self.piece_num is None:
            self.piece_num = int(self.get_length() / self.get_piece_length())
            if self.get_length() % self.get_piece_length() is not 0:
                self.piece_num += 1

        return self.piece_num


class MInfo(BaseInfo):

    class File(object):
        def __init__(self, owner, file):
            self.owner = owner
            self.file = file

        def get_length(self):
            return self.file.get(b'length')

        def get_md5sum(self):
            return self.file.get(b'md5sum')

        def get_path(self):
            path = b''
            for item in self.file.get(b'path'):
                path += (item + b'/')
            return path[:-1]

        def get_full_path(self):
            return self.owner.get_name() + b'/' + self.get_path()

    @staticmethod
    def create(info: dict):
        return MInfo(info) if BaseInfo.get_file_mode(info) == BaseInfo.FILE_MODE.MULTI else None

    def __init__(self, info: dict):
        super(MInfo, self).__init__(info)
        self.file_mode = BaseInfo.FILE_MODE.MULTI
        self.files = self.info.get(b'files')
        self.length = None
        self.piece_num = None
        self.last_piece_length = None

    def get_file_mode(self):
        return self.file_mode

    def get_name(self):
        return self.info.get(b'name')

    def get_length(self):
        if self.length is None:
            self.length = 0
            for file in self.files:
                self.length += file.get(b'length')

        return self.length

    def get_file(self, index):
        return MInfo.File(self, self.files[index]) if 0 <= index < len(self.files) else None

    def iter_files(self):
        for file in self.files:
            yield MInfo.File(self, file)

    def get_piece_num(self):
        if self.piece_num is None:
            self.piece_num = int(self.get_length() / self.get_piece_length())
            if self.get_length() % self.get_piece_length() is not 0:
                self.piece_num += 1

        return self.piece_num








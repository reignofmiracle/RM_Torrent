import math
import struct

from TorrentPython.PeerMessage import Message


class BitfieldExt(object):

    HAVE_NOT = 0
    HAVE = 1

    @staticmethod
    def create_with_bitfield_message(piece_num, msg):
        if piece_num < 0 or msg is None or msg.id != Message.BITFIELD:
            return None

        if math.ceil(piece_num / 8) != len(msg.bitfield):
            return None

        bitfield_ext = BitfieldExt(piece_num)
        for index in range(piece_num):
            if msg.have(index):
                bitfield_ext.set_have(index)

        return bitfield_ext

    @staticmethod
    def create_with_missing_piece_indices(piece_num, missing_piece_indices: set):
        if piece_num < 0 or (len(missing_piece_indices) > 0 and piece_num <= max(missing_piece_indices)):
            return None

        bitfield_ext = BitfieldExt(piece_num)
        for index in range(piece_num):
            if index not in missing_piece_indices:
                bitfield_ext.set_have(index)

        return bitfield_ext

    @staticmethod
    def create_with_completed_piece_indices(piece_num, completed_piece_indices: set):
        if piece_num < 0 or piece_num <= max(completed_piece_indices):
            return None

        bitfield_ext = BitfieldExt(piece_num)
        for index in range(piece_num):
            if index not in completed_piece_indices:
                bitfield_ext.set_have(index)

        return bitfield_ext

    def __init__(self, piece_num):
        self.bitfield = [BitfieldExt.HAVE_NOT for _ in range(piece_num)]

    def get_piece_num(self):
        return len(self.bitfield)

    def get_bitfield(self):
        return self.bitfield

    def set_have(self, index):
        if 0 <= index < len(self.bitfield):
            self.bitfield[index] = BitfieldExt.HAVE

    def have(self, index):
        return self.bitfield[index] == BitfieldExt.HAVE if 0 <= index < len(self.bitfield) else False

    def get_missing_piece_indices(self):
        missing_piece_indices = set()
        for i, v in enumerate(self.bitfield):
            if v == BitfieldExt.HAVE_NOT:
                missing_piece_indices.add(i)

        return missing_piece_indices

    def get_completed_piece_indices(self):
        completed_piece_indices = set()
        for i, v in enumerate(self.bitfield):
            if v == BitfieldExt.HAVE:
                completed_piece_indices.add(i)

        return completed_piece_indices

    def get_percent(self):
        return (sum(self.bitfield) / len(self.bitfield)) * 100

    def is_completed(self):
        return sum(self.bitfield) == len(self.bitfield)

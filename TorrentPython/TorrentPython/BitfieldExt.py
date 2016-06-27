import math

from TorrentPython.PeerMessage import Message


class BitfieldExt(object):

    @staticmethod
    def create_with_bitfield_message(piece_num, msg):
        if piece_num < 0 or msg is None or msg.id != Message.BITFIELD:
            return None

        if math.ceil(piece_num / 8) != len(msg.bitfield):
            return None

        return BitfieldExt(piece_num, msg.bitfield)

    @staticmethod
    def create_with_missing_piece_indices(piece_num, missing_piece_indices: set):
        if piece_num < 0 or piece_num <= max(missing_piece_indices):
            return None

        bitfield = BitfieldExt.create_bitfield(piece_num, lambda index: 0 if index in missing_piece_indices else 1)
        return BitfieldExt(piece_num, bitfield)

    @staticmethod
    def create_with_completed_piece_indices(piece_num, completed_piece_indices: set):
        if piece_num < 0 or piece_num <= max(completed_piece_indices):
            return None

        bitfield = BitfieldExt.create_bitfield(piece_num, lambda index: 1 if index in completed_piece_indices else 0)
        return BitfieldExt(piece_num, bitfield)

    @staticmethod
    def create_bitfield(piece_num, setter):
        bitfield = [0 for _ in range(math.ceil(piece_num / 8))]
        for index in range(piece_num):
            BitfieldExt.set_value(bitfield, index, setter(index))
        return bitfield

    @staticmethod
    def get_value(bitfield, index):
        if index < 0 or index >= len(bitfield) * 8:
            return None

        bytePos = int(index / 8)
        bitPos = index % 8

        sourceByte = bitfield[bytePos]
        targetByte = 0x80 >> bitPos

        return 1 if sourceByte & targetByte else 0

    @staticmethod
    def set_value(bitfield, index, value):
        if index < 0 or index >= len(bitfield) * 8:
            return False

        bytePos = int(index / 8)
        bitPos = index % 8

        if value == 0:
            targetByte = ~(0x80 >> bitPos)
            bitfield[bytePos] &= targetByte
        else:
            targetByte = 0x80 >> bitPos
            bitfield[bytePos] |= targetByte

        return True

    def __init__(self, piece_num, bitfield):
        self.piece_num = piece_num
        self.bitfield = bitfield

    def get_piece_num(self):
        return self.piece_num

    def get_bitfield(self):
        return self.bitfield

    def have(self, index):
        if index < 0 or index >= self.piece_num:
            return False

        return BitfieldExt.get_value(self.bitfield, index) == 1

    def get_missing_piece_indices(self):
        missing_piece_indices = set()
        for index in range(self.piece_num):
            if self.have(index) is False:
                missing_piece_indices.add(index)

        return missing_piece_indices

    def get_completed_piece_indices(self):
        completed_piece_indices = set()
        for index in range(self.piece_num):
            if self.have(index) is True:
                completed_piece_indices.add(index)

        return completed_piece_indices

    def get_percent(self):
        completed_piece_indices = self.get_completed_piece_indices()
        return (len(completed_piece_indices) / self.piece_num) * 100

    def is_completed(self):
        missing_piece_indices = self.get_missing_piece_indices()
        return len(missing_piece_indices) == 0

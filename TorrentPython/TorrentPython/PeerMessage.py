import struct

from TorrentPython.Defines import *


class Handshake(object):
    TOTAL_LEN = 68

    @staticmethod
    def getBytes(info_hash: bytes, peer_id: bytes):
        if len(info_hash) != 20 or len(peer_id) != 20:
            return None

        pstrlen = struct.pack('!B', len(Defines.PROTOCOL_ID))
        pstr = Defines.PROTOCOL_ID
        reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'

        return pstrlen + pstr + reserved + info_hash + peer_id

    @staticmethod
    def isThis(buf: bytes):
        if len(buf) is not Handshake.TOTAL_LEN:
            return False

        if struct.unpack('>B', buf[0:0 + 1])[0] != len(Defines.PROTOCOL_ID):
            return False

        if buf[1:1 + len(Defines.PROTOCOL_ID)] != Defines.PROTOCOL_ID:
            return False

        return True

    @staticmethod
    def create(buf: bytes):
        if not Handshake.isThis(buf):
            return None

        ret = Handshake()
        ret.pstrlen = buf[0:0 + 1]
        ret.pstr = buf[1:1 + 19]
        ret.reserved = buf[20:20 + 8]
        ret.info_hash = buf[28:28 + 20]
        ret.peer_id = buf[48:48 + 20]
        return ret

    def __init__(self):
        self.pstrlen = None
        self.pstr = None
        self.reserved = None
        self.info_hash = None
        self.peer_id = None


class Message(object):
    LEN_OFFSET = 0
    LEN_SIZE = 4

    ID_OFFSET = LEN_OFFSET + LEN_SIZE
    ID_SIZE = 1

    PAYLOAD_OFFSET = LEN_SIZE + ID_SIZE

    KEEP_ALIVE = None
    CHOCK = 0
    UNCHOCK = 1
    INTERESTED = 2
    NOT_INTERESTED = 3
    HAVE = 4
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7
    CANCEL = 8
    PORT = 9

    @staticmethod
    def create(buf: bytes):
        if len(buf) < Message.LEN_SIZE:
            return None

        message_len = struct.unpack('!I', buf[Message.LEN_OFFSET:Message.LEN_SIZE])[0]
        if message_len is 0:
            message_id = None
            message_buf = buf[:4]
        else:
            if len(buf) < Message.LEN_SIZE + message_len:
                return None

            message_id = struct.unpack('!B', buf[Message.ID_OFFSET:Message.ID_OFFSET + Message.ID_SIZE])[0]
            message_buf = buf[:Message.LEN_SIZE + message_len]

        return Message(message_len, message_id, message_buf)

    @staticmethod
    def getClass(message_id):
        if message_id == Message.KEEP_ALIVE:
            return KeepAlive
        if message_id == Message.CHOCK:
            return Chock
        elif message_id == Message.UNCHOCK:
            return Unchock
        elif message_id == Message.INTERESTED:
            return Interested
        elif message_id == Message.NOT_INTERESTED:
            return NotInterested
        elif message_id == Message.HAVE:
            return Have
        elif message_id == Message.BITFIELD:
            return Bitfield
        elif message_id == Message.REQUEST:
            return Request
        elif message_id == Message.PIECE:
            return Piece
        elif message_id == Message.CANCEL:
            return Cancel
        elif message_id == Message.PORT:
            return Port
        else:
            return None

    @staticmethod
    def parse(buf: bytes):
        msg = Message.create(buf)
        if msg is None:
            return None, buf

        messageClass = Message.getClass(msg.id)
        if messageClass is None:
            return None, buf

        return messageClass.create(msg.buf), buf[len(msg.buf):]

    def __init__(self, message_len, message_id, message_buf):
        self.len = message_len
        self.id = message_id
        self.buf = message_buf


class KeepAlive(Message):
    MESSAGE = b'\x00\x00\x00\x00'

    @staticmethod
    def getBytes():
        return KeepAlive.MESSAGE

    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.KEEP_ALIVE:
            return None

        obj = KeepAlive(msg.len, msg.id, msg.buf)
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(KeepAlive, self).__init__(message_len, message_id, message_buf)

    def __repr__(self):
        return 'KeepAlive'


class Chock(Message):
    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.CHOCK:
            return None

        obj = Chock(msg.len, msg.id, msg.buf)
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(Chock, self).__init__(message_len, message_id, message_buf)

    def __repr__(self):
        return 'Chock'


class Unchock(Message):
    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        return Unchock(msg.len, msg.id, msg.buf) if msg.id == Message.UNCHOCK else None

    def __init__(self, message_len, message_id, message_buf):
        super(Unchock, self).__init__(message_len, message_id, message_buf)

    def __repr__(self):
        return 'Unchock'


class Interested(Message):
    @staticmethod
    def getBytes():
        return b'\x00\x00\x00\x01\x02'

    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.INTERESTED:
            return None

        obj = Interested(msg.len, msg.id, msg.buf)
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(Interested, self).__init__(message_len, message_id, message_buf)

    def __repr__(self):
        return 'Interested'


class NotInterested(Message):
    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.NOT_INTERESTED:
            return None

        obj = NotInterested(msg.len, msg.id, msg.buf)
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(NotInterested, self).__init__(message_len, message_id, message_buf)

    def __repr__(self):
        return 'NotInterested'


class Have(Message):
    @staticmethod
    def getBytes(index):
        message_len = struct.pack('!I', 5)
        message_id = struct.pack('!B', Message.HAVE)
        message_payload = struct.pack('!I', index)
        return message_len + message_id + message_payload


class Bitfield(Message):
    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.BITFIELD:
            return None

        obj = Bitfield(msg.len, msg.id, msg.buf)
        obj.bitfield = msg.buf[Message.PAYLOAD_OFFSET:]
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(Bitfield, self).__init__(message_len, message_id, message_buf)
        self.bitfield = b''

    def __repr__(self):
        return 'Bitfield'


class Request(Message):
    MESSAGE_LEN = 1 + 4 + 4 + 4  # id, index, begin, length

    @staticmethod
    def getBytes(index, begin, length):
        message_len = struct.pack('!I', Request.MESSAGE_LEN)
        message_id = struct.pack('!B', Message.REQUEST)
        message_content = struct.pack('!III', index, begin, length)
        return message_len + message_id + message_content


class Piece(Message):
    INDEX_OFFSET = Message.LEN_SIZE + Message.ID_SIZE
    INDEX_SIZE = 4

    BEGIN_OFFSET = INDEX_OFFSET + INDEX_SIZE
    BEGIN_SIZE = 4

    BLOCK_OFFSET = BEGIN_OFFSET + BEGIN_SIZE

    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.PIECE:
            return None

        obj = Piece(msg.len, msg.id, msg.buf)
        obj.index = struct.unpack('!I', msg.buf[Piece.INDEX_OFFSET: Piece.INDEX_OFFSET + Piece.INDEX_SIZE])[0]
        obj.begin = struct.unpack('!I', msg.buf[Piece.BEGIN_OFFSET: Piece.BEGIN_OFFSET + Piece.BEGIN_SIZE])[0]
        obj.block = msg.buf[Piece.BLOCK_OFFSET:]
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(Piece, self).__init__(message_len, message_id, message_buf)
        self.index = 0
        self.begin = 0
        self.block = b''

    def __repr__(self):
        return 'Piece'


class Cancel(Message):
    @staticmethod
    def create(buf: bytes):
        msg = Message.create(buf)
        if msg.id is not Message.CANCEL:
            return None

        obj = Cancel(msg.len, msg.id, msg.buf)
        return obj

    def __init__(self, message_len, message_id, message_buf):
        super(Cancel, self).__init__(message_len, message_id, message_buf)

    def __repr__(self):
        return 'Cancel'


class Port(Message):
    pass

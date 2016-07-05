import pykka
from functools import partial
import copy

from TorrentPython.MetaInfo import *
from TorrentPython.BitfieldExt import *


class PieceAssemblerActor(pykka.ThreadingActor):

    @staticmethod
    def prepare_file(info, file_path, file_length):
        dirname = os.path.dirname(file_path)
        if os.path.isdir(dirname):
            if os.path.exists(file_path):
                if os.path.getsize(file_path) == file_length:
                    return True
                else:
                    os.remove(file_path)
        else:
            os.makedirs(dirname)

        piece_length = info.get_piece_length()
        piece_num = int(file_length / piece_length)
        with open(file_path, 'wb') as f:
            for index in range(0, piece_num):
                f.write(b' ' * piece_length)
            else:
                f.write(b' ' * (file_length % piece_length))

        return True

    @staticmethod
    def prepare_container(info, path):
        if info is None or not os.path.isdir(path):
            return False

        if info.get_file_mode() == BaseInfo.FILE_MODE.SINGLE:
            filePath = path + '/' + info.get_name().decode()
            return PieceAssemblerActor.prepare_file(info, filePath, info.get_length())

        else:
            for file in info.iter_files():
                filePath = path + file.get_full_path().decode()
                if not PieceAssemblerActor.prepare_file(info, filePath, file.get_length()):
                    return False
            return True

    @staticmethod
    def iter_pieces(info, path):
        piece_length = info.get_piece_length()

        if info.get_file_mode() == BaseInfo.FILE_MODE.SINGLE:
            with open(path + info.get_name().decode(), 'rb') as fp:
                for piece in iter(partial(fp.read, piece_length), b''):
                    yield piece
        else:
            remain = b''
            for file in info.iter_files():
                with open(path + file.get_full_path().decode(), 'rb') as fp:
                    if len(remain) > 0:
                        yield remain + fp.read(piece_length - len(remain))

                    for piece in iter(partial(fp.read, piece_length), b''):
                        if len(piece) == piece_length:
                            yield piece
                        else:
                            remain = piece
            else:
                if len(remain) > 0:
                    yield remain

    @staticmethod
    def verify(info, index, piece):
        return hashlib.sha1(piece).digest() == info.get_pieces()[index * 20: index * 20 + 20]

    @staticmethod
    def get_coverage(info, piece_index, piece_block):
        if not info.is_valid(piece_index) or info.get_piece_length_index(piece_index) != len(piece_block):
            return None

        piece_length = info.get_piece_length()
        if info.get_file_mode() == BaseInfo.FILE_MODE.SINGLE:
            item = {b'path': info.get_name(),
                    b'offset': piece_length * piece_index,
                    b'block': piece_block}
            return [item]
        else:
            items = []
            sum_of_file_length = 0
            piece_offset = piece_length * piece_index

            block_length = len(piece_block)
            block_offset = 0

            for file in info.iter_files():
                sum_of_file_length += file.get_length()
                if sum_of_file_length < piece_offset:
                    continue

                coverage_length = sum_of_file_length - (piece_offset + block_offset)
                if coverage_length < len(piece_block) - block_offset:
                    consumed = coverage_length
                else:
                    consumed = len(piece_block) - block_offset

                item = {b'path': file.get_full_path(),
                        b'offset': file.get_length() - coverage_length,
                        b'block': piece_block[block_offset: block_offset + consumed]}
                items.append(item)

                block_offset += consumed
                if block_offset == block_length:
                    break

            return items

    def __init__(self, metainfo: MetaInfo, path):
        super(PieceAssemblerActor, self).__init__()
        self.metainfo = metainfo
        self.path = path
        self.info = self.metainfo.get_info()

        self.bitfield_ext = None

        PieceAssemblerActor.prepare_container(self.info, self.path)
        self.prepare_bitfield_ext()

    def prepare_bitfield_ext(self):
        missing_piece_indices = set()
        for index, piece in enumerate(PieceAssemblerActor.iter_pieces(self.info, self.path)):
            if not PieceAssemblerActor.verify(self.info, index, piece):
                missing_piece_indices.add(index)

        self.bitfield_ext = BitfieldExt.create_with_missing_piece_indices(
            self.info.get_piece_num(), missing_piece_indices)

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def get_bitfield_ext(self):
        return copy.deepcopy(self.bitfield_ext)

    def write(self, piece_index, piece_block):
        coverage_plan = PieceAssemblerActor.get_coverage(self.info, piece_index, piece_block)
        if not coverage_plan:
            return False

        for plan in coverage_plan:
            with open(self.path + plan[b'path'].decode(), 'rb+') as f:
                f.seek(plan[b'offset'])
                f.write(plan[b'block'])

        self.bitfield_ext.set_have(piece_index)
        return True


class PieceAssembler(object):

    @staticmethod
    def start(metainfo: MetaInfo, path):
        return PieceAssembler(metainfo, path)

    def __init__(self, metainfo: MetaInfo, path):
        self.actor = PieceAssemblerActor.start(metainfo, path)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive():
            self.actor.stop()

    def get_bitfield_ext(self):
        return self.actor.ask({'func': 'get_bitfield_ext', 'args': None})

    def write(self, piece_index, piece_block):
        return self.actor.ask({'func': 'write', 'args': (piece_index, piece_block)})

import pykka
from functools import partial

from TorrentPython.MetaInfo import *


class PieceAssemblerCore(pykka.ThreadingActor):

    @staticmethod
    def prepare_file(metainfo: MetaInfo, file_path, file_length):
        dirname = os.path.dirname(file_path)
        if os.path.isdir(dirname):
            if os.path.exists(file_path):
                if os.path.getsize(file_path) == file_length:
                    return True
                else:
                    os.remove(file_path)
        else:
            os.makedirs(dirname)

        info = metainfo.get_info()
        piece_length = info.get_piece_length()
        piece_num = int(file_length / piece_length)
        with open(file_path, 'wb') as f:
            for index in range(0, piece_num):
                f.write(b' ' * piece_length)
            else:
                f.write(b' ' * (file_length % piece_length))

        return True

    @staticmethod
    def prepare_container(metainfo: MetaInfo, path):
        if metainfo is None or not os.path.isdir(path):
            return False

        info = metainfo.get_info()
        if info.get_file_mode() == BaseInfo.FILE_MODE.SINGLE:
            filePath = path + '/' + info.get_name().decode()
            return PieceAssemblerCore.prepare_file(metainfo, filePath, info.get_length())

        else:
            for file in info.iter_files():
                filePath = path + file.get_full_path().decode()
                if not PieceAssemblerCore.prepare_file(metainfo, filePath, file.get_length()):
                    return False
            return True

    @staticmethod
    def iter_pieces(metainfo: MetaInfo, path):
        info = metainfo.get_info()
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
    def verify(metainfo: MetaInfo, index, piece):
        return hashlib.sha1(piece).digest() == metainfo.get_info().get_pieces()[index * 20: index * 20 + 20]

    @staticmethod
    def get_coverage(metainfo: MetaInfo, piece_index, piece_block):
        info = metainfo.get_info()
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
        super(PieceAssemblerCore, self).__init__()
        self.metainfo = metainfo
        self.path = path

    def on_receive(self, message):
        return message.get('func')(self)

    def prepare(self):
        return PieceAssemblerCore.prepare_container(self.metainfo, self.path)

    def get_missing_piece_indices(self):
        missing_piece_indices = []
        for index, piece in enumerate(PieceAssemblerCore.iter_pieces(self.metainfo, self.path)):
            if not PieceAssemblerCore.verify(self.metainfo, index, piece):
                missing_piece_indices.append(index)

        return missing_piece_indices

    def write(self, piece_index, piece_block):
        coverage_plan = PieceAssemblerCore.get_coverage(self.metainfo, piece_index, piece_block)
        if not coverage_plan:
            return False

        for plan in coverage_plan:
            with open(self.path + plan[b'path'].decode(), 'rb+') as f:
                f.seek(plan[b'offset'])
                f.write(plan[b'block'])

        return True


class PieceAssembler(object):
    def __init__(self, metainfo: MetaInfo, path):
        self.core = PieceAssemblerCore.start(metainfo, path)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.core.is_alive():
            self.core.stop()

    def prepare(self):
        return self.core.ask({'func': lambda x: x.prepare()})

    def get_missing_piece_indices(self):
        return self.core.ask({'func': lambda x: x.get_missing_piece_indices()})

    def write(self, piece_index, piece_block):
        return self.core.ask({'func': lambda x: x.write(piece_index, piece_block)})

import os
import shutil

from TorrentPython.MetaInfo import *


class FileManager(object):

    @staticmethod
    def prepareFile(filePath, fileLength):
        dirname = os.path.dirname(filePath)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        if os.path.exists(filePath):
            if os.path.getsize(filePath) == fileLength:
                return True
            else:
                os.remove(filePath)

        with open(filePath, 'wb') as f:
            f.write(b' ' * fileLength)

        return True

    @staticmethod
    def prepareContainer(metainfo: MetaInfo, path):
        if metainfo is None or not os.path.isdir(path):
            return False

        info = metainfo.get_info()
        if info.getFileMode() == BaseInfo.FILE_MODE.SINGLE:
            filePath = path + '/' + info.getName().decode()
            return FileManager.prepareFile(filePath, info.getLength())

        else:
            for file in info.getFiles():
                filePath = path + info.getName().decode() + '/' + file.getFullPath().decode()
                if not FileManager.prepareFile(filePath, file.getLength()):
                    return False
            return True

    def __init__(self, metainfo: MetaInfo, path):
        self.metainfo = metainfo
        self.path = path
        self.prepared = False

    def prepare(self):
        self.prepared = FileManager.prepareContainer(self.metainfo, self.path)
        return self.prepared

    def write(self, piece_index, piece_block):
        if not self.prepared:
            return False

        return True

    def getMissingPieceIndices(self):
        info = self.metainfo.get_info()
        if info.getFileMode() == BaseInfo.FILE_MODE.SINGLE:
            pass
        else:
            pass

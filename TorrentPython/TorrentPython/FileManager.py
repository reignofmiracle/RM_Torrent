import os
import shutil

from TorrentPython.MetaInfo import *


class FileManager(object):

    def __init__(self, metainfo: MetaInfo, path):
        self.metainfo = metainfo
        self.path = path

    def checkCastle(self):
        pass

    def buildCastle(self, clear=False):
        if not self.fence(clear):
            return False

        return True

    def fence(self, clear):
        if os.path.isdir(self.path):
            if clear:
                shutil.rmtree(self.path)
            else:
                return False

        os.mkdir(self.path)
        return True

    def write(self, piece: tuple):
        pass

    def getMissingPieceIndices(self):
        pass

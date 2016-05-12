from TorrentPython.MetaInfoManager import *

import hashlib
import urllib.request
import urllib.parse


class TrackerManager(object):

    @staticmethod
    def CreateFromMagnet(magnetStr):
        return None

    @staticmethod
    def CreateFromTorrent(torrentPath):
        metaInfo = MetaInfoManager.parseFromTorrent(torrentPath)
        bencoded_info = MetaInfoManager.getInfoHashFromTorrent(torrentPath)
        if metaInfo is None or bencoded_info is None:
            return None

        ret = TrackerManager()
        ret.metaInfo = metaInfo
        ret.info_hash = bencoded_info
        return ret       

    def __init__(self):
        self.metaInfo = None
        self.info_hash = None
        self.peer_id = '2dd1dbc742ad47b3b83c'
        self.ip = None
        self.port = 6881
        self.uploaded = None
        self.downloaded = None
        self.left = None
        self.event = None

    def requestInfo(self, announce=None):
        if announce is None:
            announce = self.metaInfo[b'announce'].decode('UTF-8')        

        print(announce)

        params = '?' + urllib.parse.urlencode(
            {urllib.parse.quote('info_hash') : urllib.parse.quote(self.getInfoHash(), safe='%'),
             urllib.parse.quote('peer_id') : urllib.parse.quote(self.peer_id, safe='%'),
             urllib.parse.quote('port') : self.port,
             urllib.parse.quote('uploaded') : 0,
             urllib.parse.quote('downloaded') : 0,
             urllib.parse.quote('left') : 0,
             urllib.parse.quote('event') : ''},
            encoding='utf-8', safe='%')

        request = urllib.request.Request(announce + params, method='GET')
        return urllib.request.urlopen(request).read()

    def getInfoHash(self):
        return self.info_hash

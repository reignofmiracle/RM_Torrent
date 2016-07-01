import urllib.request

from TorrentPython.TrackerProtocol import *


class TrackerService(object):

    @staticmethod
    def request(url, info_hash, client_id, port):
        params = TrackerProtocol.get_request(info_hash, client_id, port)
        request = urllib.request.Request(url + params, method='GET')
        return urllib.request.urlopen(request).read()

class DownloadStatus(object):
    def __init__(self, bitfield_ext, download_speed, peer_size):
        self.bitfield_ext = bitfield_ext
        self.download_speed = download_speed
        self.peer_size = peer_size

    def __repr__(self):
        return 'DownloadStatus : {} %, {} MB/s, {} peers'.format(
            self.bitfield_ext.get_percent(), self.download_speed, self.peer_size)

class DownloadStatus(object):
    def __init__(self, bitfield_ext, download_speed):
        self.bitfield_ext = bitfield_ext
        self.download_speed = download_speed

    def __repr__(self):
        return '{}, {} %, {} MB/s'.format('DownloadStatus', self.bitfield_ext.get_percent(), self.download_speed)

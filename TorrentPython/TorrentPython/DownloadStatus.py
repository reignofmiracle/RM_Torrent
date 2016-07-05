class DownloadStatus(object):
    def __init__(self):
        self.elapsed_time = 0  # sec
        self.bitfield_ext = None
        self.download_speed = 0  # kB/s
        self.peer_size = 0

    def __repr__(self):
        return 'DownloadStatus : {} s, {} %, {} kB/s, {} peers'.format(
            self.elapsed_time,
            self.bitfield_ext.get_percent(),
            self.download_speed,
            self.peer_size)

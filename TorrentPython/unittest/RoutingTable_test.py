import unittest
from TorrentPython.RoutingTable import RoutingTable

ROUTING_TABLE = {b'wO\x9fo\xf9\x17\x04}\xe5\x07\x10\xfb\xfc\x19|UW\xf3\x88\xb3': ('98.235.207.101', 29599),
                      b'g\xa2^\r\xca\xech{\x1d["w\xed\xd7\';`\x7fh\x0c': ('186.155.142.157', 10044),
                      b'OO\x105#\xed\x84_\xbf8\xe2\xa6\xa5\x92\xb2\xfe_(\x8b\x13': ('200.175.83.182', 14967),
                      b'i\x9d\xea\xf8\xf9/\xd9b\xab\xbd(\xb4t^?4p\x1c\xe4\x7f': ('216.228.213.11', 57810),
                      b'i\xb3{ Y\x03\x01\x9f]@\x8c\xae\x93\xaeT\xc0\xbf\xf4s\xa9': ('118.161.50.249', 9838),
                      b'w\x14=t\xac\x98\x8e/\xb2#P\xfaYZh\xbd8\x87\xc9&': ('36.239.195.195', 25685),
                      b'i\x98J\n\x7f\xdb\xfd]]\x02B\x02\xe8q.\xc1|;u\xc6': ('153.160.192.32', 6889),
                      b'i\x90\xacu\xe1\xad\x1b*\xf4q\x1fK"\x1ah\xc2?F\x12\xdb': ('184.172.56.6', 6887),
                      b'i\x90\xab_\xb3\x05\x17\x82\xe6AY\x99W\xb7\x01t\xcfV\x02\x1b': ('184.172.56.6', 6917),
                      b'h =6\xab}N\xb8\x1fr-\xd5l\'"\xe1x0\'\xee': ('151.248.162.88', 6889),
                      b'i\x8fLx\xfd\xbdBQ~]:&\x03\xfb\x1b\x93\xd2\x94\x7f\x17': ('85.97.213.172', 15347),
                      b'J)\x11\x0f\xc2\xc3S\x81[\xf6~\xc0J\x07\x97\xfbV\xc3\\[': ('73.249.94.45', 26085),
                      b'i\x83\xd8\xbb\x87L\xb0\xdd\xfd\x95\x12@t\x8fNP<\x95b\xba': ('112.163.221.45', 52109),
                      b'\x007F\xd6\xaeR\x90I\xf1\xf1\xbb\xe9\xeb\xb3\xa6\xdb<\x87\x0c\xe1': ('68.114.132.220', 36673),
                      b'i\x9a\xac8s%92\x0f&4\x07\xcc\xb1\xf7\xa29\xb27\x80': ('144.76.102.212', 24049),
                      b'\x8d\xb1S*D+\xb3\xf8\xc4b\xd7\xeb\x1c\xad%\xdeXC\xe5\xd8': ('91.121.59.153', 6881),
                      b'i\x9d\xf1-\x9eb\xcb\x1f.\x93K<C\xb6\x1aZ\x8c0\xccq': ('73.68.249.26', 8999),
                      b'%\xac\x18\xd6\xaeR\x90I\xf1\xf1\xbb\xe9\xeb\xb3\xa6\xdb<\x87\x0c\xe1': ('114.77.186.175', 35984),
                      b'NX\xc0*.\xb3\xb2\x04u\x85\xed\xe5\xfd\xdac\x9d/z\xc6\x9a': ('118.168.22.205', 7662),
                      b'i\x93\xc0j\x0b\xce\x9f|\xb6S\x0ed\xd3\x87\x05,IB\xc2\xa9': ('50.97.82.39', 6889),
                      b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g': ('67.215.246.10', 6881),
                      b"h,\x81\xa40\x08\xc1\x9a-\x02\x06\xf1#\x1f\x10\xcc\xcdx'\x0c": ('98.114.101.66', 6889),
                      b'\x1aV\x83QtyQ\xa1\xc2\x00o4b\xb4\xd2\xe8\x97\x02Tz': ('14.176.54.48', 2124),
                      b'i\x9b\xa2\xa6\xaa\xf6=W\xea}\x12\xd6\xb7~\x19\xe7O\x8c\xa3\xff': ('207.190.116.8', 43342),
                      b'i\xb6\x84\x1e\xbf3_\x14\xa2k\xdb\x83\xc1\xed\x1bBr\x1e"\xca': ('36.237.63.142', 8792),
                      b'\xeb\xff6isQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g': ('82.221.103.244', 6881),
                      b'EMBB0D59D62708FXXX\xfa\x84': ('58.19.0.194', 3306),
                      b'i\xd2\xb0\xcdP\xc17t\xcd\x16\xa5@\x7f@F\x85\xe6\nu\xea': ('61.60.222.90', 8596),
                      b'k\xd6\xf57d\xa0N\x11\x93\x1b\t\xa2\xdb\x95\xe8X\x02\x8a\x0e,': ('110.23.94.112', 23758),
                      b'i\x88Ted\x1b\x94\xfa"\xc5\xf6|J\xcbru\n5\xc4\xba': ('107.152.100.2', 6915),
                      b"\x007G\xa7\x13}\x04\x91G\x92o'V\x9d<\x80Y\xf8I\x1e": ('58.253.49.15', 11101),
                      b'\x7f\xc3\xfehG\x02\xb9\x0f\t\xda\x1bp\x96g\x1d\xacY\xf4H\xd5': ('61.243.37.239', 8322),
                      b'h\xcf\xa2\x0e\xbe\x8a\xc3\x99\xbcpO\x19\xe1\xdf\xbb\xa8\xf7k\x05\x83': ('118.8.66.175', 6889),
                      b'i\xfd\xf7-\xb3\xad\x8f(\x94\xd6\xed\xc8\xc6K\xaeb\x9a(Qv': ('66.172.193.33', 1030),
                      b'h\xe6\xa1\x96U\x18\x8a\xa7\xae\xf9r\xc1\xbb\xbdt}\xb8u\x88w': ('61.231.31.222', 9362),
                      b'hv\xc3\xccD\x12\x91\xe2\xb8}\xbbOB\xaaJ\x9c\xc6\x02MA': ('106.70.202.51', 11101),
                      b'=m\xc5\xd9\x0fHV\xd5\x86\xbe#\xad\xf7d\xb7\x0f\x04f\xee\xb5': ('189.195.175.254', 48102),
                      b'i5\xa7#\xcfs\xbe\xa8;\x82\xdb\xb1>\\\xe5\r\xff\xdb\\\r': ('121.208.213.139', 10513),
                      b'i\x90\xa8m\x04\xc35y\x13\xa5\xb8}\x91\x94 \x01\\17\xbb': ('184.172.56.6', 6948),
                      b'@\xf2\xd7\xe3\x8c\xb2R\xe8\xb6\xcfg\xa0\xe5|\xf9gY\x03\xf2\x8f': ('46.139.82.178', 38240),
                      b"i\x8b;59\x19\xcb\x07*\x1d\x88\xef|p\xd9q\xe2-['": ('123.202.123.240', 11101),
                      b'i\x9d\xed\xecg\x03\x1f\xc9\xb4\xbd\xff\xbe\xa1O\xbd\x8b\x17S\xd2e': ('113.230.55.144', 11101),
                      b'X\xe5\x9cX#\xb8\xe8\xd0&\xdc\x06\x90\xc6_\xc1}\x1a3\xe8\xb0': ('42.117.106.36', 1024)}

ROUTING_TABLE_PATH = '../Resources/routing_table.py'


class RoutingTableTest(unittest.TestCase):
    def setUp(self):
        self.routing_table = ROUTING_TABLE
        self.routing_table_path = ROUTING_TABLE_PATH
        pass

    def tearDown(self):
        pass

    # @unittest.skip("clear")
    def test_save(self):
        RoutingTable.save(self.routing_table, self.routing_table_path)
        ret = RoutingTable.load(self.routing_table_path)
        self.assertEqual(self.routing_table, ret)

if __name__ == '__main__':
    unittest.main()

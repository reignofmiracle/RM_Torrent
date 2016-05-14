import unittest

from TorrentPython.DHTExplorer import *

INFO_HASH = b'i\x9c\xda\x89Z\xf6\xfb\xd5\xa8\x17\xff\xf4\xfeo\xa8\xab\x87\xe3oH'


class DHTExplorerTest(unittest.TestCase):
    def setUp(self):
        #self.routingTable = {DHTService.INITIAL_NODE_ID: (DHTService.INITIAL_NODE_IP, DHTService.INITIAL_NODE_PORT)}
        self.routingTable = {b'\xfdiP\xca\xc1\xde\xef1\xfb\x1d\xaa\xdb\xb0)G\x03yE\xcb*': ('130.204.98.239', 16763), b'\xf8\xd9\xdc\x94I\xeali\x9aa\xbe\x0e\xb3\xb9k=\x00\r\xbe+': ('159.203.7.75', 52272), b'i\x94DM\xb9\x00Z\x8e\xd1\xd7e\x9e\x83\x17(\x97\x123l\xb7': ('114.26.3.240', 8246), b'\x0b<q\xe7\xf4t.\xc3i:\xad\x11]\x03\x9f\x90"+\x03\x0f': ('89.189.177.199', 7115), b'k\xcb\xa8\x87\x14|\x89Bi+\xb3gP\xb1\xac\x13\xc5-\xefn': ('85.86.109.232', 48182), b'i\xa1\x9ed\xa2\xc6\xb5\n\x12\x92<\xf1)/\x01\n\xe0>p\xb3': ('202.125.20.114', 26148), b'i\x04\x9dO\xcb\xb6\x96D\x0bm\xea\xf4\x81le\xa9g\xf5\x11\xfa': ('192.131.44.26', 6881), b'\xf5\xaa2\xb4 \xc4l`\x08\xb1\x9c\xc6\xae$|$\x1f\x1e\xd3p': ('37.113.41.244', 19745), b'i\x89\xe0\x1d\xb8\xa7\x08\x0cy\xf7\x9d\xfc\xd8\x89\x14M\x05\xe1\xb3\xaf': ('85.11.180.174', 37239), b'h\xf9p\x0e\xdc\xf0w\x1c\x1fb\x04\xf3\xb9\xe6\xb6U:&\x03\x15': ('95.211.168.13', 6881), b'i0\x05\xf8\xfa\xd4P\xb46\x13\x01\x9c\xca\xb2TN\xeb\xe0O\x0b': ('84.24.85.195', 11894), b'h\xb0\r#\xb2&k\x93\x02\xf9\xc7\xb9N\xa3&\xa7\xdc\xe8\x83R': ('37.187.99.114', 51413), b'h\x03\x9c\x87\xd39\xd5\x85\x1f\xc6"\x06\x9d\x84\x7fk?o\x88+': ('67.82.208.10', 15849), b'i\x9fk\x14\xf2D@f\xd0k\xc40\xb72;\xa1"\xf6"\xad': ('65.110.218.37', 58786), b'h\xc1\x80\x89\x87K\xf9n=9<\xbdJd\x04\xc5R/>M': ('37.142.34.19', 34966), b"i\xa6]!C|U\xe1\x93&l'e\x06\xceb\xcd\xa1Q\x11": ('58.27.175.19', 64523), b'i\xba\x83&\xd1\xf8|\xb6\xab\x14pG\xef\x9d\x14\xdb\xec\xb8\xca1': ('185.35.37.224', 34100), b'h\x86\x19}>)E\x15y)\xce=c\xad\xaf\x9cR\xdex\x08': ('178.32.115.69', 6881), b'<[\x82\x977\xab\x1f\xf3\xc7\xe7\x01\xab\xed^l/\x01\xfe=e': ('31.55.97.160', 21322), b'i\x94\xc1\xf0\xffOW\x06\x95?\xaf\xc5D\xb2\x18\x85Q\xe9\x9e\x14': ('90.154.69.213', 56963), b'r\x82{p\x03L[$\r\xd7Y\x95r\xbf-\xd12St\xd6': ('98.238.164.37', 36120), b'i\x87\xca\xa3\xbf\xd2\xca\x1fNC\xf8d\xa6l\xed\x82\xf9\xaa\xdb\r': ('81.200.30.97', 51413), b'i\xa8M\xfc\xd2\x04}\x94\x9e!\xf6z\x1cq^c\xef\x16\xf9#': ('89.166.116.88', 51413), b'\x07sf\xb2\x07\xaf\x88\xfb\nk\x8d\x12\xe4tC\xfdN2\xcf\xe4': ('93.77.119.220', 56090), b'i\xbe\x0b\xc1\xf4\x9e\xedyxn\xaa\xd0X?Tp-\xa8z}': ('31.28.217.234', 54293), b'i\x8d\xa8\x06\xcc\xa8?\xe6\xd9\xbb\x96p\xd59\x01\xbb\x8b\x94\xbe\xb9': ('89.212.105.117', 56619), b'i\xae\x89\x81Q\xe9\x19\x0b\xa2\xd0z\x82\xd0\x90\x9e\xac\x11?\\\xd5': ('5.228.255.246', 61083), b'i]\x96\x8eu\xdc?\x7f\xf9\x8a\xc8n\xcbt,\x18\x88R\x98v': ('93.159.238.49', 14638), b'<\x83\xbdv\x95\xd50\r\xfd+E\xe0\x86\xa0\xf1\xb9\x9d\xfa\xd0\xc2': ('93.170.146.67', 13780), b'K\xa7\xcd0c\xc41X\xa9f\rz\xec\xadI\x06\xc3\x9eW0': ('77.85.137.23', 41740)}
        pass

    def tearDown(self):
        pass

    # @unittest.skip("wait")
    def test_findPeers(self):
        DHTService.TIMEOUT_SEC = 1 # sec

        service = DHTService()
        peers, routingTable = DHTExplorer.findPeers(service, self.routingTable, INFO_HASH)
        self.assertTrue(len(peers) > 0)
        self.assertTrue(len(routingTable) > 0)

        pass

    @unittest.skip("clear")
    def findPeersFromRoutingTable(self):
        service = DHTService()
        peers, routingTable = DHTExplorer.findPeersFromRoutingTable(service, self.routingTable, INFO_HASH)
        self.assertTrue(len(routingTable) > 0)
        print(peers)
        print(routingTable)

if __name__ == '__main__':
    unittest.main()



class DHTExplorer(object):

    @staticmethod
    def create():
        return DHTExplorer()

    @staticmethod
    def createBaseRouteTable(routeTable):
        return None

    def __init__(self):
        self.routeTable = {}

    def findPeers(self, size=10, depth=0, time=10):
        return None

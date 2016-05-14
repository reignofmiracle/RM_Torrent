import time
import types

from TorrentPython.DHTService import *


class DHTExplorer(object):

    NODE_EXPANSION_SIZE = 10

    @staticmethod
    def findPeers(service: DHTService, routingTable: dict, info_hash: bytes, peerLimit=5, timeLimit=5):
        if service is None or routingTable is None or info_hash is None:
            return [], routingTable

        updatedRoutingTable = dict(routingTable)
        workingTable = dict(routingTable)

        peerLimitChecker = DHTExplorer.generatePeerLimitChecker(peerLimit)
        timeLimitChecker = DHTExplorer.generateTimeLimitChecker(timeLimit)

        peers = []
        while len(workingTable) > 0 and not peerLimitChecker(len(peers)):
            retPeers, workingTable = DHTExplorer.findPeersFromRoutingTable(
                service, workingTable, info_hash, peerLimitChecker, timeLimitChecker)
            peers.extend(retPeers)

            updatedRoutingTable = DHTExplorer.updateRoutingTable(updatedRoutingTable, workingTable, info_hash)

            if timeLimitChecker():
                break

        return peers, updatedRoutingTable

    @staticmethod
    def findPeersFromRoutingTable(service: DHTService, routingTable: dict, info_hash: bytes,
                                  peerLimitChecker: types.FunctionType, timeLimitChecker: types.FunctionType):
        if service is None or routingTable is None or info_hash is None:
            return [], routingTable

        if peerLimitChecker is None or timeLimitChecker is None:
            return [], routingTable

        peers = []
        updatedRoutingTable = {}

        for k, v in routingTable.items():
            response = service.getPeers((socket.gethostbyname(v[0]), v[1]), info_hash)
            if response is None or DHTService.isResponseError(response):
                continue

            if DHTService.isResponsePeers(response):
                peers.extend(DHTService.parsePeers(response))
                if peerLimitChecker(len(peers)):
                    break
            else:
                updatedRoutingTable.update(DHTService.parseNodes(response))

            if timeLimitChecker():
                break

        return peers, updatedRoutingTable

    @staticmethod
    def updateRoutingTable(routingTable: dict, workingTable: dict, info_hash: bytes):
        updatedRoutingTable = dict(routingTable)

        intersect = [key for key in workingTable if key in updatedRoutingTable]
        for key in intersect:
            del workingTable[key]

        count = 0
        for key in sorted(workingTable, key=lambda v: bytes((a ^ b) for a, b in zip(info_hash, v))):
            updatedRoutingTable[key] = workingTable[key]

            count += 1
            if count >= DHTExplorer.NODE_EXPANSION_SIZE:
                break

        return updatedRoutingTable

    @staticmethod
    def generatePeerLimitChecker(peerLimit):
        if peerLimit <= 0:
            return lambda v: False
        else:
            return lambda v: v >= peerLimit

    @staticmethod
    def generateTimeLimitChecker(timeLimit):
        if timeLimit <= 0:
            return lambda: False
        else:
            sTime = time.clock()
            return lambda: time.clock() - sTime > timeLimit





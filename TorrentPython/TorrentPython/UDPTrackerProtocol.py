import struct

CONNECTION_ID = 0x41727101980


class Connecting(object):
    def __init__(self, action, transaction_id):
        self.connection_id = CONNECTION_ID
        self.action = action
        self.transaction_id = transaction_id

    def getPacket(self):
        return struct.pack('>QLL', self.connection_id, self.action, self.transaction_id)


class ConnectingResponse(object):
    def __init__(self, response):
        self.action, self.transaction_id, self.connection_id = \
                     struct.unpack('>LLQ', response)[0]
        
        


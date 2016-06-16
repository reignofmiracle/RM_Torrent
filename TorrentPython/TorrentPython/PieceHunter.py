import threading

from TorrentPython.PeerRadio import *


class PieceHunterMessage(object):
    CONNECTED = 'CONNECTED'
    DISCONNECTED = 'DISCONNECTED'
    PIECE = 'PIECE'
    COMPLETED = 'COMPLETED'
    INTERRUPTED = 'INTERRUPTED'

    def __init__(self, message_id, message_payload):
        self.id = message_id
        self.payload = message_payload

    @staticmethod
    def connected():
        return PeerRadioMessage(PieceHunterMessage.CONNECTED, None)

    @staticmethod
    def disconnected():
        return PeerRadioMessage(PieceHunterMessage.DISCONNECTED, None)

    @staticmethod
    def piece(index, piece):
        return PeerRadioMessage(PieceHunterMessage.PIECE, (index, piece))

    @staticmethod
    def completed():
        return PeerRadioMessage(PieceHunterMessage.COMPLETED, None)

    @staticmethod
    def interrupted():
        return PeerRadioMessage(PieceHunterMessage.INTERRUPTED, None)


class PieceHunterCore(pykka.ThreadingActor):
    INVALID_PIECE_INDEX = -1
    PIECE_PER_STEP = 7

    def __init__(self, piece_hunter, client_id: bytes, metainfo: MetaInfo):
        super(PieceHunterCore, self).__init__()
        self.piece_hunter = piece_hunter
        self.client_id = client_id
        self.metainfo = metainfo
        self.info = metainfo.get_info()

        self.peer_radio = PeerRadio(client_id, metainfo)
        self.peer_radio.subscribe(on_next=self.on_next)

        self.cleanup()

    def cleanup(self):
        self.piece_indices = None
        self.piece_per_step = PieceHunterCore.PIECE_PER_STEP
        self.timeout = None

        self.piece_queue = None
        self.workingPiece_index = PieceHunterCore.INVALID_PIECE_INDEX
        self.workingPiece = b''
        self.workingStep = 0
        self.delayTimer = None

    def on_start(self):
        pass

    def on_stop(self):
        self.peer_radio.destroy()
        self.piece_hunter.on_completed()

    def on_receive(self, message):
        return message.get('func')(self)

    def on_next(self, msg):
        if msg.id == PeerRadioMessage.CONNECTED:
            self.piece_hunter.on_next(PieceHunterMessage.connected())

        elif msg.id == PeerRadioMessage.DISCONNECTED:
            self.piece_hunter.on_next(PieceHunterMessage.disconnected())

        elif msg.id == PeerRadioMessage.RECEIVED:
            payload = msg.payload
            if payload.id == Message.UNCHOCK:
                self.actor_ref.tell({'func': lambda x: x.request()})

            elif payload.id == Message.PIECE:
                self.actor_ref.tell({'func': lambda x: x.update(payload)})

    def request(self):
        if self.peer_radio.getChock():
            return False

        if len(self.piece_queue) > 0:
            if int(len(self.piece_queue) / self.piece_per_step) > 0:
                self.workingStep = self.piece_per_step
            else:
                self.workingStep = len(self.piece_queue) % self.piece_per_step

            for i in range(0, self.workingStep):
                index = self.piece_queue[i]
                piece_length = self.info.getPieceLength_index(index)

                block_num = int(piece_length / PeerRadioCore.BLOCK_SIZE)
                block_remain = piece_length % PeerRadioCore.BLOCK_SIZE
                for j in range(0, block_num):
                    self.peer_radio.request(index, j * PeerRadioCore.BLOCK_SIZE, PeerRadioCore.BLOCK_SIZE)
                if block_remain > 0:
                    self.peer_radio.request(index, block_num * PeerRadioCore.BLOCK_SIZE, block_remain)

            self.start_timer()

    def update(self, msg):
        if msg.index == self.workingPiece_index:
            if msg.begin == len(self.workingPiece):
                self.workingPiece += msg.block
            else:
                self.out_error('piece middle error.')
                return False

            expectLength = self.info.getPieceLength_index(self.workingPiece_index)
            if expectLength == len(self.workingPiece):
                self.piece_hunter.on_next(PieceHunterMessage.piece(self.workingPiece_index, self.workingPiece))
                self.piece_queue.remove(self.workingPiece_index)
                self.workingPiece_index = PieceHunterCore.INVALID_PIECE_INDEX
                self.workingPiece = b''

                if len(self.piece_queue) == 0:
                    self.piece_hunter.on_next(PieceHunterMessage.completed())
                    self.cleanup()
                else:
                    self.workingStep -= 1
                    if self.workingStep == 0:
                        self.request()
        else:
            if self.workingPiece_index == PieceHunterCore.INVALID_PIECE_INDEX:
                if msg.begin == 0:
                    self.workingPiece_index = msg.index
                    self.workingPiece = msg.block
                else:
                    self.piece_hunter.on_next(PieceHunterMessage.interrupted())
                    self.cleanup()
                    return False
            else:
                self.piece_hunter.on_next(PieceHunterMessage.interrupted())
                self.cleanup()
                return False

        return True

    def discard(self):
        self.cleanup()
        self.piece_hunter.on_next(PieceHunterMessage.interrupted())

    def start_timer(self):
        if self.delayTimer is not None:
            self.delayTimer.cancel()

        self.delayTimer = threading.Timer(self.timeout, self.check_timeout_async)
        self.delayTimer.start()

    def check_timeout_async(self):
        if self.actor_ref.is_alive():
            self.actor_ref.tell({'func': lambda x: x.check_timeout()})

    def check_timeout(self):
        if len(self.piece_queue) > 0:
            self.discard()

    def connect(self, peer_ip, peer_port):
        return self.peer_radio.connect(peer_ip, peer_port)

    def disconnect(self):
        return self.peer_radio.disconnect()

    def hunt(self, piece_indices: list, piece_per_step, timeout):
        if self.piece_queue:
            return False

        self.cleanup()

        self.piece_indices = piece_indices
        self.piece_per_step = piece_per_step
        self.timeout = timeout

        self.piece_queue = piece_indices.copy()

        self.request()
        return True


class PieceHunter(Subject):

    def __init__(self, client_id: bytes, metainfo: MetaInfo):
        super(PieceHunter, self).__init__()
        self.core = PieceHunterCore.start(self, client_id, metainfo)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.core.is_alive():
            self.core.stop()

    def connect(self, peer_ip, peer_port):
        return self.core.ask({'func': lambda x: x.connect(peer_ip, peer_port)})

    def disconnect(self):
        return self.core.ask({'func': lambda x: x.disconnect()})

    def hunt(self, piece_indices: list, piece_per_step, timeout):
        self.core.tell({'func': lambda x: x.hunt(piece_indices, piece_per_step, timeout)})


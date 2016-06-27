import threading

from TorrentPython.BitfieldExt import BitfieldExt
from TorrentPython.PeerRadio import *


class PieceRadioMessage(object):
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
        return PeerRadioMessage(PieceRadioMessage.CONNECTED, None)

    @staticmethod
    def disconnected():
        return PeerRadioMessage(PieceRadioMessage.DISCONNECTED, None)

    @staticmethod
    def piece(index, piece):
        return PeerRadioMessage(PieceRadioMessage.PIECE, (index, piece))

    @staticmethod
    def completed():
        return PeerRadioMessage(PieceRadioMessage.COMPLETED, None)

    @staticmethod
    def interrupted():
        return PeerRadioMessage(PieceRadioMessage.INTERRUPTED, None)


class PieceRadioActor(pykka.ThreadingActor):
    INVALID_PIECE_INDEX = -1
    PIECE_PER_STEP = 7

    def __init__(self, piece_radio, client_id: bytes, metainfo: MetaInfo):
        super(PieceRadioActor, self).__init__()
        self.piece_radio = piece_radio
        self.client_id = client_id
        self.metainfo = metainfo
        self.info = metainfo.get_info()

        self.peer_radio = PeerRadio(client_id, metainfo)
        self.peer_radio.subscribe(on_next=self.on_next)

        self.cleanup()

    def cleanup(self):
        self.bitfield_ext = None
        self.piece_indices = None
        self.piece_per_step = PieceRadioActor.PIECE_PER_STEP
        self.timeout = None

        self.piece_queue = None
        self.working_piece_index = PieceRadioActor.INVALID_PIECE_INDEX
        self.working_piece = b''  # rm_notice
        self.workingStep = 0
        self.delay_timer = None

    def on_start(self):
        pass

    def on_stop(self):
        self.peer_radio.destroy()
        self.piece_radio.on_completed()

    def on_receive(self, message):
        return message.get('func')(self)

    def on_next(self, msg):
        if msg.id == PeerRadioMessage.CONNECTED:
            self.piece_radio.on_next(PieceRadioMessage.connected())

        elif msg.id == PeerRadioMessage.DISCONNECTED:
            self.piece_radio.on_next(PieceRadioMessage.disconnected())

        elif msg.id == PeerRadioMessage.RECEIVED:
            payload = msg.payload
            if payload.id == Message.UNCHOCK:
                self.actor_ref.tell({'func': lambda x: x.request()})

            elif payload.id == Message.BITFIELD:
                self.bitfield_ext = BitfieldExt.create_with_bitfield_message(payload)

            elif payload.id == Message.PIECE:
                self.actor_ref.tell({'func': lambda x: x.update(payload)})

    def request(self):
        if self.peer_radio.get_chock():
            return False

        if len(self.piece_queue) > 0:
            if int(len(self.piece_queue) / self.piece_per_step) > 0:
                self.workingStep = self.piece_per_step
            else:
                self.workingStep = len(self.piece_queue) % self.piece_per_step

            for i in range(0, self.workingStep):
                index = self.piece_queue[i]
                piece_length = self.info.get_piece_length_index(index)

                block_num = int(piece_length / PeerRadioActor.BLOCK_SIZE)
                block_remain = piece_length % PeerRadioActor.BLOCK_SIZE
                for j in range(0, block_num):
                    self.peer_radio.request(index, j * PeerRadioActor.BLOCK_SIZE, PeerRadioActor.BLOCK_SIZE)
                if block_remain > 0:
                    self.peer_radio.request(index, block_num * PeerRadioActor.BLOCK_SIZE, block_remain)

            self.start_timer()

    def update(self, msg):
        if msg.begin == len(self.working_piece):
            if self.working_piece_index in (msg.index, PieceRadioActor.INVALID_PIECE_INDEX):
                self.working_piece_index = msg.index
                self.working_piece += msg.block

                if self.info.get_piece_length_index(self.working_piece_index) == len(self.working_piece):
                    self.piece_radio.on_next(PieceRadioMessage.piece(self.working_piece_index, self.working_piece))
                    self.piece_queue.remove(self.working_piece_index)
                    self.working_piece_index = PieceRadioActor.INVALID_PIECE_INDEX
                    self.working_piece = b''

                    if len(self.piece_queue) == 0:
                        self.piece_radio.on_next(PieceRadioMessage.completed())
                        self.cleanup()
                    else:
                        self.workingStep -= 1
                        if self.workingStep == 0:
                            self.request()

                return True

        self.piece_radio.on_next(PieceRadioMessage.interrupted())
        self.cleanup()
        return False

    def discard(self):
        self.cleanup()
        self.piece_radio.on_next(PieceRadioMessage.interrupted())

    def start_timer(self):
        if self.delay_timer is not None:
            self.delay_timer.cancel()

        self.delay_timer = threading.Timer(self.timeout, self.check_timeout_async)
        self.delay_timer.start()

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

    def get_bitfield_ext(self):
        return self.bitfield_ext

    def from_request(self, piece_indices: list, piece_per_step, timeout):
        if self.piece_queue:
            return False

        self.cleanup()

        self.piece_indices = piece_indices
        self.piece_per_step = piece_per_step
        self.timeout = timeout

        self.piece_queue = piece_indices.copy()

        self.request()
        return True


class PieceRadio(Subject):

    def __init__(self, client_id: bytes, metainfo: MetaInfo):
        super(PieceRadio, self).__init__()
        self.actor = PieceRadioActor.start(self, client_id, metainfo)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def connect(self, peer_ip, peer_port):
        return self.actor.ask({'func': lambda x: x.connect(peer_ip, peer_port)})

    def disconnect(self):
        return self.actor.ask({'func': lambda x: x.disconnect()})

    def get_bitfield_ext(self):
        return self.actor.ask({'func': lambda x: x.get_bitfield_ext()})

    def request(self, piece_indices: list, piece_per_step, timeout):
        self.actor.tell({'func': lambda x: x.from_request(piece_indices, piece_per_step, timeout)})

import threading

from TorrentPython.PeerRadio import *


class PieceRadioActor(pykka.ThreadingActor):
    INVALID_PIECE_INDEX = -1
    PIECE_PER_STEP = 7
    PEER_RADIO_TIMEOUT = 30  # sec

    def __init__(self, piece_radio, client_id: bytes, metainfo: MetaInfo):
        super(PieceRadioActor, self).__init__()
        self.piece_radio = piece_radio
        self.client_id = client_id
        self.metainfo = metainfo
        self.info = metainfo.get_info()

        self.peer_radio = PeerRadio.start(client_id, metainfo)
        self.peer_radio.subscribe(on_next=self.on_subscribe)

        self.piece_per_step = PieceRadioActor.PIECE_PER_STEP
        self.peer_radio_timeout = PieceRadioActor.PEER_RADIO_TIMEOUT

        self.chock = True  # reset at disconnected

        self.piece_indices = None
        self.piece_queue = None
        self.working_piece_index = PieceRadioActor.INVALID_PIECE_INDEX
        self.working_piece = b''  # rm_notice
        self.working_step = 0
        self.delay_timer = None

    def cleanup(self):
        self.piece_indices = None
        self.piece_queue = None
        self.working_piece_index = PieceRadioActor.INVALID_PIECE_INDEX
        self.working_piece = b''  # rm_notice
        self.working_step = 0

        if self.delay_timer is not None:
            self.delay_timer.cancel()
            self.delay_timer = None

    def on_stop(self):
        self.peer_radio.stop()
        self.cleanup()
        self.piece_radio.on_completed()

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def on_subscribe(self, msg):
        if self.actor_ref.is_alive():
            self.actor_ref.tell({'func': 'on_next', 'args': (msg,)})

    def on_next(self, msg):
        if msg.get('id') == 'connected':
            self.piece_radio.on_next(msg)

        elif msg.get('id') == 'disconnected':
            self.piece_radio.on_next(msg)

        elif msg.get('id') == 'msg':
            payload = msg.get('payload')

            if payload.id == Message.CHOCK:
                self.chock = True

            elif payload.id == Message.UNCHOCK:
                self.chock = False
                self.on_request()

            elif payload.id == Message.BITFIELD:
                bitfield_ext = BitfieldExt.create_with_bitfield_message(self.info.get_piece_num(), payload)
                self.piece_radio.on_next({'id': 'bitfield', 'payload': bitfield_ext})

            elif payload.id == Message.PIECE:
                self.on_update(payload)

    def on_request(self):
        if self.chock is True or self.piece_queue is None or len(self.piece_queue) <= 0:
            return

        if int(len(self.piece_queue) / self.piece_per_step) > 0:
            self.working_step = self.piece_per_step
        else:
            self.working_step = len(self.piece_queue) % self.piece_per_step

        for i in range(0, self.working_step):
            index = self.piece_queue[i]
            piece_length = self.info.get_piece_length_index(index)

            block_num = int(piece_length / PeerRadioActor.BLOCK_SIZE)
            block_remain = piece_length % PeerRadioActor.BLOCK_SIZE
            for j in range(0, block_num):
                self.peer_radio.request(index, j * PeerRadioActor.BLOCK_SIZE, PeerRadioActor.BLOCK_SIZE)
            if block_remain > 0:
                self.peer_radio.request(index, block_num * PeerRadioActor.BLOCK_SIZE, block_remain)

        self.start_timer()

    def on_update(self, msg):
        self.start_timer()

        if msg.begin == len(self.working_piece):
            if self.working_piece_index in (msg.index, PieceRadioActor.INVALID_PIECE_INDEX):
                self.working_piece_index = msg.index
                self.working_piece += msg.block

                if self.info.get_piece_length_index(self.working_piece_index) == len(self.working_piece):
                    self.piece_radio.on_next({'id': 'piece', 'payload': (self.working_piece_index, self.working_piece)})
                    self.piece_queue.remove(self.working_piece_index)
                    self.working_piece_index = PieceRadioActor.INVALID_PIECE_INDEX
                    self.working_piece = b''

                    if len(self.piece_queue) == 0:
                        self.piece_radio.on_next({'id': 'completed', 'payload': None})
                        self.cleanup()
                    else:
                        self.working_step -= 1
                        if self.working_step == 0:
                            self.on_request()

                return True

        self.interrupted()

    def interrupted(self):
        self.piece_radio.on_next({'id': 'interrupted', 'payload': self.piece_queue})
        self.cleanup()

    def start_timer(self):
        if self.delay_timer is not None:
            self.delay_timer.cancel()

        self.delay_timer = threading.Timer(self.peer_radio_timeout, self.check_timeout_async)
        self.delay_timer.start()

    def check_timeout_async(self):
        if self.actor_ref.is_alive():
            self.actor_ref.tell({'func': 'check_timeout', 'args': None})

    def check_timeout(self):
        if self.piece_queue and len(self.piece_queue) > 0:
            self.interrupted()

    def set_piece_per_step(self, piece_per_step):
        self.piece_per_step = piece_per_step

    def set_peer_radio_timeout(self, peer_radio_timeout):
        self.peer_radio_timeout = peer_radio_timeout

    def connect(self, peer_ip, peer_port):
        self.peer_radio.connect(peer_ip, peer_port)

    def disconnect(self):
        self.peer_radio.disconnect()
        self.chock = True

    def from_request(self, piece_indices: list):
        self.cleanup()
        self.piece_indices = piece_indices
        self.piece_queue = piece_indices.copy()
        self.on_request()


class PieceRadio(Subject):

    @staticmethod
    def start(client_id: bytes, metainfo: MetaInfo):
        return PieceRadio(client_id, metainfo)

    def __init__(self, client_id: bytes, metainfo: MetaInfo):
        super(PieceRadio, self).__init__()
        self.actor = PieceRadioActor.start(self, client_id, metainfo)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive():
            self.actor.stop()

    def set_piece_per_step(self, piece_per_step):
        self.actor.tell({'func': 'set_piece_per_step', 'args': (piece_per_step,)})

    def set_peer_radio_timeout(self, peer_radio_timeout):
        self.actor.tell({'func': 'set_peer_radio_timeout', 'args': (peer_radio_timeout,)})

    def connect(self, peer_ip, peer_port):
        self.actor.tell({'func': 'connect', 'args':(peer_ip, peer_port)})

    def disconnect(self):
        self.actor.tell({'func': 'disconnect', 'args': None})

    def request(self, piece_indices: list):
        self.actor.tell({'func': 'from_request', 'args': (piece_indices,)})

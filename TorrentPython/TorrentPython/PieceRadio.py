import threading

from TorrentPython.PeerRadio import *


class PieceRadioActor(pykka.ThreadingActor):
    REQUEST_QUEUE_DEFAULT_SIZE = 5
    REQUEST_QUEUE_EXPANSION_SIZE = 5
    REQUEST_AGAIN_TIMEOUT = 20

    def __init__(self, piece_radio, client_id: bytes, metainfo: MetaInfo):
        super(PieceRadioActor, self).__init__()
        self.piece_radio = piece_radio
        self.client_id = client_id
        self.metainfo = metainfo
        self.info = metainfo.get_info()

        self.peer_radio = PeerRadio.start(client_id, metainfo)
        self.peer_radio.subscribe(on_next=self.on_subscribe)

        self.chock = True  # reset at disconnected

        self.request_again_timer = None
        self.peer_ip = None
        self.peer_port = None
        self.piece_indices = None
        self.piece_orders = None
        self.piece_storage = None
        self.request_queue_size = PieceRadioActor.REQUEST_QUEUE_DEFAULT_SIZE
        self.request_orders = None
        self.request_prepared = False

    def cleanup(self):
        if self.request_again_timer:
            self.request_again_timer.cancel()

        self.peer_ip = None
        self.peer_port = None
        self.piece_indices = None
        self.piece_orders = None
        self.piece_storage = None
        self.request_queue_size = PieceRadioActor.REQUEST_QUEUE_DEFAULT_SIZE
        self.request_orders = None
        self.request_prepared = False

    def prepare_request(self, piece_indices: list):
        if self.request_prepared is True:
            return False

        if piece_indices is None or len(piece_indices) <= 0:
            return False

        self.piece_indices = piece_indices

        self.piece_orders = []
        for index in self.piece_indices:
            piece_length = self.info.get_piece_length_index(index)
            for begin in range(0, piece_length, PeerRadioActor.BLOCK_SIZE):
                self.piece_orders.append((index, begin, PeerRadioActor.BLOCK_SIZE))
            else:
                last_begin = begin + PeerRadioActor.BLOCK_SIZE
                remain = piece_length - last_begin
                if remain:
                    self.piece_orders.append((index, last_begin, remain))

        self.piece_storage = {}
        for index in self.piece_indices:
            piece_length = self.info.get_piece_length_index(index)
            block_num = math.ceil(piece_length / PeerRadioActor.BLOCK_SIZE)
            self.piece_storage[index] = [None for _ in range(block_num)]

        self.request_orders = []
        self.request_prepared = True

        return True

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
            self.on_disconnected(msg)

        elif msg.get('id') == 'msg':
            payload = msg.get('payload')

            if payload.id == Message.CHOCK:
                self.chock = True

            elif payload.id == Message.UNCHOCK:
                self.chock = False
                self.on_request()
                self.piece_radio.on_next({'id': 'unchock', 'payload': None})

            elif payload.id == Message.BITFIELD:
                bitfield_ext = BitfieldExt.create_with_bitfield_message(self.info.get_piece_num(), payload)
                self.piece_radio.on_next({'id': 'bitfield', 'payload': bitfield_ext})

            elif payload.id == Message.HAVE:
                self.piece_radio.on_next({'id': 'have', 'payload': payload.index})

            elif payload.id == Message.PIECE:
                self.on_update(payload)

    def on_disconnected(self, msg):
        self.chock = True
        self.piece_orders = self.request_orders + self.piece_orders
        self.request_queue_size -= PieceRadioActor.REQUEST_QUEUE_EXPANSION_SIZE

        if self.request_queue_size > 0:
            if self.peer_radio.connect(self.peer_ip, self.peer_port):
                return

        if self.piece_storage:
            self.piece_radio.on_next({'id': 'interrupted', 'payload': list(self.piece_storage.keys())})
        self.cleanup()
        self.piece_radio.on_next(msg)

    def on_request(self):
        if self.chock is True or self.request_prepared is False:
            return False

        self.request_orders = self.piece_orders[:self.request_queue_size]
        self.piece_orders = self.piece_orders[self.request_queue_size:]

        for order in self.request_orders:
            self.peer_radio.request(*order)

        self.start_request_again_timer()

        return True

    def on_update(self, msg):
        order = (msg.index, msg.begin, len(msg.block))
        if order not in self.request_orders:
            return False

        self.request_orders.remove(order)

        storage = self.piece_storage.get(msg.index)
        block_index = int(msg.begin / PeerRadioActor.BLOCK_SIZE)
        storage[block_index] = msg.block

        if all(storage):
            self.piece_radio.on_next({'id': 'piece', 'payload': (msg.index, b''.join(storage))})
            self.piece_storage.pop(msg.index)
            self.peer_radio.have(msg.index)

            if len(self.piece_storage) == 0:
                if self.request_again_timer:
                    self.request_again_timer.cancel()
                self.cleanup()
                self.piece_radio.on_next({'id': 'completed', 'payload': None})

        if not self.request_orders and self.piece_orders:
            self.request_queue_size += PieceRadioActor.REQUEST_QUEUE_EXPANSION_SIZE
            self.on_request()

        self.start_request_again_timer()

        return True

    def start_request_again_timer(self):
        if self.request_again_timer:
            self.request_again_timer.cancel()

        self.request_again_timer = threading.Timer(
            PieceRadioActor.REQUEST_AGAIN_TIMEOUT,
            lambda: self.actor_ref.tell({'func': 'request_again', 'args': None}))
        self.request_again_timer.start()

    def request_again(self):
        self.piece_orders = self.request_orders + self.piece_orders
        self.on_request()

    def is_prepared(self):
        return self.request_prepared

    def connect(self, peer_ip, peer_port):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        return self.peer_radio.connect(peer_ip, peer_port)

    def disconnect(self):
        return self.peer_radio.disconnect()

    def from_request(self, piece_indices: list):
        if self.prepare_request(piece_indices):
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
            self.actor.tell({'func': 'stop', 'args': None})

    def is_prepared(self):
        return self.actor.ask({'func': 'is_prepared', 'args': None})

    def connect(self, peer_ip, peer_port):
        return self.actor.ask({'func': 'connect', 'args':(peer_ip, peer_port)})

    def disconnect(self):
        return self.actor.ask({'func': 'disconnect', 'args': None})

    def request(self, piece_indices: list):
        self.actor.tell({'func': 'from_request', 'args': (piece_indices,)})

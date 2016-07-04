from TorrentPython.PieceRadio import *


class PieceHunterActor(pykka.ThreadingActor):
    DEFAULT_REQUEST_ORDER_SIZE = 5

    def __init__(self, piece_hunter, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port):
        super(PieceHunterActor, self).__init__()
        self.piece_hunter = piece_hunter
        self.hunting_scheduler = hunting_scheduler  # DI
        self.piece_assembler = piece_assembler  # DI
        self.client_id = client_id
        self.metainfo = metainfo
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.piece_radio = PieceRadio.start(self.client_id, self.metainfo)
        self.piece_radio.subscribe(on_next=self.on_subscribe)

        self.request_order_size = PieceHunterActor.DEFAULT_REQUEST_ORDER_SIZE
        self.connected = False
        self.bitfield_ext = None

    def on_stop(self):
        self.piece_radio.stop()
        self.piece_hunter.on_completed()

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def on_subscribe(self, msg):
        if self.actor_ref.is_alive():
            self.actor_ref.tell({'func': 'on_next', 'args': (msg,)})

    def on_next(self, msg):
        if msg.get('id') == 'connected':
            self.connected = True

        elif msg.get('id') == 'disconnected':
            self.connected = False
            self.piece_hunter.on_completed()

        elif msg.get('id') == 'bitfield':
            self.bitfield_ext = msg.get('payload')
            self.download()

        elif msg.get('id') == 'piece':
            self.piece_assembler.write(*msg.get('payload'))
            self.hunting_scheduler.complete_order(msg.get('payload')[0])
            self.piece_hunter.on_next({'id': 'downloaded', 'payload': msg.get('payload')[0]})

        elif msg.get('id') == 'completed':
            self.download()

        elif msg.get('id') == 'interrupted':
            for order in msg.get('payload'):
                self.hunting_scheduler.cancel_order(order)
            self.piece_hunter.on_completed()

    def set_request_order_size(self, request_order_size):
        self.request_order_size = request_order_size

    def get_uid(self):
        return self.peer_ip, self.peer_port

    def connect(self):
        return self.piece_radio.connect(self.peer_ip, self.peer_port)

    def download(self):
        if self.connected and self.bitfield_ext:
            order_list = self.hunting_scheduler.get_order_list(
                self.bitfield_ext, self.request_order_size)
            if len(order_list) > 0:
                self.piece_radio.request(order_list)
            else:
                self.piece_hunter.on_completed()


class PieceHunter(Subject):

    @staticmethod
    def start(hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port):
        return PieceHunter(hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port)

    def __init__(self, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port):
        super(PieceHunter, self).__init__()
        self.actor = PieceHunterActor.start(
            self, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive() is True:
            self.actor.tell({'func': 'stop', 'args': None})

    def set_request_order_size(self, request_order_size):
        return self.actor.ask({'func': 'set_request_order_size', 'args': (request_order_size,)})

    def get_uid(self):
        return self.actor.ask({'func': 'get_uid', 'args': None})

    def connect(self):
        self.actor.tell({'func': 'connect', 'args': None})

    def disconnect(self):
        self.actor.tell({'func': 'disconnect', 'args': None})

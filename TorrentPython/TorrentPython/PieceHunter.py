from TorrentPython.PieceRadio import *


class PieceHunterActor(pykka.ThreadingActor):
    def __init__(self, piece_hunter, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port):
        super(PieceHunterActor, self).__init__()
        self.piece_hunter = piece_hunter
        self.hunting_scheduler = hunting_scheduler  # DI
        self.piece_assembler = piece_assembler  # DI
        self.piece_radio = PieceRadio(client_id, metainfo)
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.piece_radio.subscribe(on_next=self.from_next)

    def on_stop(self):
        self.piece_radio.destroy()
        self.piece_hunter.on_completed()

    def on_receive(self, message):
        return message.get('func')(self)

    def from_next(self, msg):
        if msg.id == PieceRadioMessage.CONNECTED:
            print('connected', self.peer_ip, self.peer_port)
            self.actor_ref.tell({'func': lambda x: x.download()})

        elif msg.id == PieceRadioMessage.DISCONNECTED:
            print('disconnected', self.peer_ip, self.peer_port)
            self.piece_hunter.on_completed()

        elif msg.id == PieceRadioMessage.PIECE:
            self.piece_assembler.write(*msg.payload)
            self.hunting_scheduler.complete_order(msg.payload[0])

        elif msg.id == PieceRadioMessage.COMPLETED:
            self.actor_ref.tell({'func': lambda x: x.download()})

        elif msg.id == PieceRadioMessage.INTERRUPTED:
            for order in msg.payload:
                self.hunting_scheduler.cancel_order(order)
        self.piece_hunter.on_completed()

    def get_uid(self):
        return self.peer_ip, self.peer_port

    def connect(self):
        return self.piece_radio.connect(self.peer_ip, self.peer_port)

    def download(self):
        order_list = self.hunting_scheduler.get_order_list(
            self.piece_radio.get_bitfield_ext(), PieceHunter.REQUEST_ORDER_SIZE)
        print(order_list)
        if len(order_list) > 0:
            self.piece_radio.request(order_list)
        else:
            self.on_completed()


class PieceHunter(Subject):

    REQUEST_ORDER_SIZE = 5

    def __init__(self, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port):
        super(PieceHunter, self).__init__()
        self.actor = PieceHunterActor.start(
            self, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive() is True:
            self.actor.stop()

    def get_uid(self):
        return self.actor.ask({'func': lambda x: x.get_uid()})

    def connect(self):
        return self.actor.ask({'func': lambda x: x.connect()})

    def download(self):
        return self.actor.ask({'func': lambda x: x.download()})

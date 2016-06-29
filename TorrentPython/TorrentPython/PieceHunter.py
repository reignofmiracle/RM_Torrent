from rx.subjects import *

from TorrentPython.PieceRadio import *


class PieceHunter(Subject):

    PIECE_RADIO_TIMEOUT = 5  # sec

    def __init__(self, hunting_scheduler, piece_assembler, client_id, metainfo, peer_ip, peer_port):
        super(PieceHunter, self).__init__()
        self.hunting_scheduler = hunting_scheduler
        self.piece_assembler = piece_assembler
        self.piece_radio = PieceRadio(client_id, metainfo)
        self.peer_ip = peer_ip
        self.peer_port = peer_port

        self.piece_radio.subscribe(on_next=self.receive, on_completed=self.on_completed)
        self.piece_radio.connect(self.peer_ip, self.peer_port)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.piece_radio:
            self.piece_radio.destroy()

    def receive(self, msg):
        if msg.id == PieceRadioMessage.CONNECTED:
            self.download()

        elif msg.id == PieceRadioMessage.DISCONNECTED:
            self.on_completed()

        elif msg.id == PieceRadioMessage.PIECE:
            self.piece_assembler.write(*msg.payload)
            self.hunting_scheduler.complete_order(msg.payload[0])

        elif msg.id == PieceRadioMessage.COMPLETED:
            self.download()

        elif msg.id == PieceRadioMessage.INTERRUPTED:
            self.on_completed()

    def download(self):
        order = self.hunting_scheduler.get_order()
        print(order)
        self.piece_radio.request(order, 1, PieceHunter.PIECE_RADIO_TIMEOUT)


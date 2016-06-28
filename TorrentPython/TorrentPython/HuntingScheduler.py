import pykka
import random


class HuntingSchedulerActor(pykka.ThreadingActor):

    PIECE_DOWNLOAD_NONE = 0
    PIECE_DOWNLOAD_RUNNING = 1
    PIECE_DOWNLOAD_COMPLETED = 2

    @staticmethod
    def select_order(schedule_board: list):
        candidates = [i for i, v in enumerate(schedule_board) if v == HuntingSchedulerActor.PIECE_DOWNLOAD_NONE]
        return None if len(candidates) == 0 else random.choice(candidates)

    def __init__(self, piece_assembler):
        super(HuntingSchedulerActor, self).__init__()
        self.piece_assembler = piece_assembler

        self.schedule_board = \
            [HuntingSchedulerActor.PIECE_DOWNLOAD_NONE for _ in range(self.piece_assembler.get_piece_num())]

    def on_receive(self, message):
        return message.get('func')(self)

    def get_order(self):
        order = HuntingSchedulerActor.select_order(self.schedule_board)
        if order is not None:
            self.schedule_board[order] = HuntingSchedulerActor.PIECE_DOWNLOAD_RUNNING

        return order

    def complete_order(self, order):
        if self.schedule_board[order] == HuntingSchedulerActor.PIECE_DOWNLOAD_RUNNING:
            self.schedule_board[order] = HuntingSchedulerActor.PIECE_DOWNLOAD_COMPLETED

    def cancel_order(self, order):
        if self.schedule_board[order] == HuntingSchedulerActor.PIECE_DOWNLOAD_RUNNING:
            self.schedule_board[order] = HuntingSchedulerActor.PIECE_DOWNLOAD_NONE


class HuntingScheduler(object):

    def __init__(self, piece_assembler):
        self.actor = HuntingSchedulerActor.start(piece_assembler)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def get_order(self):
        return self.actor.ask({'func': lambda x: x.get_order()})

    def complete_order(self, order):
        self.actor.tell({'func': lambda x: x.complete_order(order)})

    def cancel_order(self, order):
        self.actor.tell({'func': lambda x: x.cancel_orders(order)})


import pykka
import random


class HuntingSchedulerActor(pykka.ThreadingActor):

    PIECE_DOWNLOAD_NONE = 0
    PIECE_DOWNLOAD_RUNNING = 1
    PIECE_DOWNLOAD_COMPLETED = 2

    @staticmethod
    def select_order(completed_piece_indices: list, schedule_board: list):
        candidates = [i for i, v in enumerate(schedule_board)
                      if v == HuntingSchedulerActor.PIECE_DOWNLOAD_NONE and i in completed_piece_indices]
        return None if len(candidates) == 0 else random.choice(candidates)

    def __init__(self, piece_assembler):
        super(HuntingSchedulerActor, self).__init__()
        self.piece_assembler = piece_assembler
        self.bitfield_ext = None
        self.schedule_board = None

    def on_start(self):
        self.bitfield_ext = self.piece_assembler.get_bitfield_ext()
        self.schedule_board = [HuntingSchedulerActor.PIECE_DOWNLOAD_COMPLETED
                               if self.bitfield_ext.have(i) else HuntingSchedulerActor.PIECE_DOWNLOAD_NONE
                               for i in range(self.bitfield_ext.get_piece_num())]

    def on_receive(self, message):
        func = getattr(self, message.get('func'))
        args = message.get('args')
        return func(*args) if args else func()

    def get_order_list(self, bitfield_ext, order_size):
        if order_size <= 0:
            return []

        if bitfield_ext:
            completed_piece_indices = bitfield_ext.get_completed_piece_indices()
        else:
            completed_piece_indices = [i for i in range(self.bitfield_ext.get_piece_num())]

        order_list = []
        for i in range(order_size):
            order = HuntingSchedulerActor.select_order(completed_piece_indices, self.schedule_board)
            if order is not None:
                self.schedule_board[order] = HuntingSchedulerActor.PIECE_DOWNLOAD_RUNNING
                order_list.append(order)
            else:
                break

        return order_list

    def complete_order(self, order):
        if self.schedule_board[order] == HuntingSchedulerActor.PIECE_DOWNLOAD_RUNNING:
            self.schedule_board[order] = HuntingSchedulerActor.PIECE_DOWNLOAD_COMPLETED

    def cancel_order(self, order):
        if self.schedule_board[order] == HuntingSchedulerActor.PIECE_DOWNLOAD_RUNNING:
            self.schedule_board[order] = HuntingSchedulerActor.PIECE_DOWNLOAD_NONE


class HuntingScheduler(object):

    @staticmethod
    def start(piece_assembler):
        return HuntingScheduler(piece_assembler)

    def __init__(self, piece_assembler):
        self.actor = HuntingSchedulerActor.start(piece_assembler)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.actor.is_alive():
            self.actor.stop()

    def get_order_list(self, bitfield_ext, order_size):
        return self.actor.ask({'func': 'get_order_list', 'args': (bitfield_ext, order_size)})

    def complete_order(self, order):
        self.actor.tell({'func': 'complete_order', 'args': (order,)})

    def cancel_order(self, order):
        self.actor.tell({'func': 'cancel_order', 'args': (order,)})


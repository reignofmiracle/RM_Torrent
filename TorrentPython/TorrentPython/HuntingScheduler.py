import pykka
from enum import Enum


class HuntingSchedulerActor(pykka.ThreadingActor):

    PIECE_DOWNLOAD_NONE = 0
    PIECE_DOWNLOAD_RUNNING = 1
    PIECE_DOWNLOAD_COMPLETED = 2

    def __init__(self, download_manager, piece_assembler):
        super(HuntingSchedulerActor, self).__init__()
        self.download_manager = download_manager
        self.piece_assembler = piece_assembler

        self.schedule_board = \
            [HuntingSchedulerActor.PIECE_DOWNLOAD_NONE for _ in range(self.piece_assembler.get_piece_num())]

    def on_receive(self, message):
        return message.get('func')(self)

    def scheduling(self, piece_num):
        pass

    def update_complete(self, orders):
        pass

    def update_drop(self, orders):
        pass

    def get_orders(self, piece_num):
        orders = self.scheduling(piece_num)
        self.update_get(orders)

    def complete_orders(self, orders: list):
        self.update_complete(orders)
        self.download_manager.update()

    def drop_orders(self, orders: list):
        self.update_drop(orders)
        self.download_manager.update()


class HuntingScheduler(object):

    def __init__(self, download_manager, piece_assembler):
        self.actor = HuntingSchedulerActor.start(download_manager, piece_assembler)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.actor.is_alive():
            self.actor.stop()

    def get_orders(self, piece_num):
        return self.actor.ask({'func': lambda x: x.get_orders(piece_num)})

    def complete_orders(self, orders: list):
        self.actor.tell({'func': lambda x: x.complete_orders(orders)})

    def drop_orders(self, orders: list):
        self.actor.tell({'func': lambda x: x.drop_orders(orders)})


import datetime
import time
import gdax


class OrderBookCustom(gdax.OrderBook):
    def is_ready(self):
        try:
            super(OrderBookCustom, self).get_ask()
        except ValueError as e:
            print(datetime.datetime.now(), e)
            return False
        return True

    def get_ask(self):
        while not self.is_ready():
            time.sleep(0.01)
        return super(OrderBookCustom, self).get_ask()

    def get_bid(self):
        while not self.is_ready():
            time.sleep(0.01)
        return super(OrderBookCustom, self).get_bid()

    def on_open(self):
        self.stop = False
        self._sequence = -1

    def on_error(self, e):
        raise e

from decimal import Decimal, ROUND_DOWN
import datetime
import time
import gdax
import config


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
        return super(OrderBookCustom, ).get_bid()

    def on_open(self):
        self.stop = False
        self._sequence = -1

    def on_error(self, e):
        raise e


def get_usd():
    try:
        for account in auth_client.get_accounts():
            if account.get('currency') == 'USD':
                return round_usd(account.get('available'))
    except AttributeError:
        return round_usd('0.0')


def get_btc():
    try:
        for account in auth_client.get_accounts():
            if account.get('currency') == 'BTC':
                return round_btc(account.get('available'))
        return round_btc(auth_client.get_accounts()[0]['available'])
    except AttributeError:
        return round_btc('0.0')


def round_usd(money):
    return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)


def round_btc(money):
    return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)


def place_buy(partial='1.0'):
    amount = get_usd() * Decimal(partial)
    bid = order_book.get_ask() - Decimal('0.01')
    amount = round_btc(Decimal(amount) / Decimal(bid))

    if amount < Decimal('0.01'):
        amount = get_usd()
        bid = order_book.get_ask() - Decimal('0.01')
        amount = round_btc(Decimal(amount) / Decimal(bid))

    if amount >= Decimal('0.01'):
        return auth_client.buy(type='limit', size=str(amount),
                                    price=str(bid), post_only=True,
                                    product_id='BTC-USD')
    else:
        ret = {'status': 'done'}
        return ret


def buy(amount=None):
    try:
        ret = place_buy('0.5')
        bid = ret.get('price')
        while ret.get('status') != 'done':
            if ret.get('status') == 'rejected' or ret.get('message') == 'NotFound':
                ret = place_buy('0.5')
                bid = ret.get('price')
            elif not bid or Decimal(bid) < order_book.get_ask() - Decimal('0.01'):
                if len(auth_client.get_orders()[0]) > 0:
                    ret = place_buy('1.0')
                else:
                    ret = place_buy('0.5')
                for order in auth_client.get_orders()[0]:
                    if order.get('id') != ret.get('id'):
                        auth_client.cancel_order(order.get('id'))
                bid = ret.get('price')
            if ret.get('id'):
                ret = auth_client.get_order(ret.get('id'))
            usd = get_usd()
        if ret.get('id'):
            auth_client.cancel_all(product_id='BTC-USD')
        usd = get_usd()
    except Exception as e:
        print(datetime.datetime.now(), e)


order_book = OrderBookCustom()
order_book.start()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
buy()

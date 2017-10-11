from decimal import Decimal
from orderbookcustom import OrderBookCustom
from currency import *
import datetime
import gdax
import config


def place_sell(partial='1.0'):
    amount = round_btc(get_btc(auth_client) * Decimal(partial))
    if amount < Decimal('0.01'):
        amount = get_btc(auth_client)
    ask = order_book.get_bid() + Decimal('0.01')

    if amount >= Decimal('0.01'):
        print("Placing sell... Price: %.2f Size: %.8f" % (ask, amount))
        return auth_client.sell(type='limit', size=str(amount),
                                price=str(ask), post_only=True,
                                product_id='BTC-USD')
    else:
        ret = {'status': 'done'}
        return ret


def sell(amount=None):
    try:
        ret = place_sell('0.5')
        ask = ret.get('price')
        btc = get_btc(auth_client)
        while btc >= Decimal('0.01') or len(auth_client.get_orders()[0]) > 0:
            if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                ret = place_sell('0.5')
                ask = ret.get('price')
            elif not ask or Decimal(ask) > order_book.get_bid() + Decimal('0.01'):
                if len(auth_client.get_orders()[0]) > 0:
                    ret = place_sell('1.0')
                else:
                    ret = place_sell('0.5')
                for order in auth_client.get_orders()[0]:
                    if order.get('id') != ret.get('id'):
                        auth_client.cancel_order(order.get('id'))
                ask = ret.get('price')
            if ret.get('id'):
                ret = auth_client.get_order(ret.get('id'))
            btc = get_btc(auth_client)
        if ret.get('id'):
            auth_client.cancel_all(product_id='BTC-USD')
        btc = get_btc(auth_client)
    except Exception as e:
        print(datetime.datetime.now(), e)


# Initialization
order_book = OrderBookCustom()
order_book.start()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
print("Initializing Order Book...")

sell()

# Cleanup
print("Sale complete!")
order_book.close()

from decimal import Decimal
from orderbookcustom import OrderBookCustom
from currency import *
import datetime
import gdax
import config


def place_buy(partial='1.0'):
    amount = get_usd(auth_client) * Decimal(partial)
    bid = order_book.get_ask() - Decimal('0.01')
    amount = round_btc(Decimal(amount) / Decimal(bid))

    if amount < Decimal('0.01'):
        amount = get_usd(auth_client)
        bid = order_book.get_ask() - Decimal('0.01')
        amount = round_btc(Decimal(amount) / Decimal(bid))

    if amount >= Decimal('0.01'):
        print("Placing buy... Price: %.2f Size: %.8f" % (bid, amount))
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
        usd = get_usd(auth_client)
        while usd > Decimal('0.0') or len(auth_client.get_orders()[0]) > 0:
            if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
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
            usd = get_usd(auth_client)
        if ret.get('id'):
            auth_client.cancel_all(product_id='BTC-USD')
        usd = get_usd(auth_client)
    except Exception as e:
        print(datetime.datetime.now(), e)


# Initialization
order_book = OrderBookCustom()
order_book.start()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
print("Initializing Order Book...")

buy()

# Cleanup
print("Buy Complete!")
order_book.close()

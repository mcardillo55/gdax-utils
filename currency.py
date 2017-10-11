from decimal import Decimal, ROUND_DOWN


def get_usd(auth_client):
    try:
        for account in auth_client.get_accounts():
            if account.get('currency') == 'USD':
                return round_usd(account.get('available'))
    except AttributeError:
        return round_usd('0.0')


def get_btc(auth_client):
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

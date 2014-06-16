from authorize.client import AuthorizeClient, AuthorizeCreditCard
from authorize.data import Address, CreditCard

from secrets import CC_AUTH


def get_client():
    return AuthorizeClient(CC_AUTH['api_id'], CC_AUTH['transaction_key'])


def get_card(card_num, cvn, exp_month, exp_year, fname, lname,
             street, city, state, zip_code, country='USA'):
    client = get_client()
    address = Address(street, city, state, zip_code, country)
    card = CreditCard(card_num, exp_year, exp_month, cvn, fname, lname)
    return AuthorizeCreditCard(client, card, address=address)


def charge_card(amount, card):
    return card.capture(amount)


def settle_transaction(transaction):
    return transaction.settle()


def authorize_card(amount, card):
    return card.auth(amount)
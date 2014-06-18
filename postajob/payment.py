from authorize.client import AuthorizeClient, AuthorizeCreditCard
from authorize.data import Address, CreditCard

from django.conf import settings


def get_client():
    return AuthorizeClient(settings.CC_AUTH['api_id'],
                           settings.CC_AUTH['transaction_key'])


def get_card(card_num, cvn, exp_month, exp_year, fname, lname,
             street, city, state, zipcode, country='USA'):
    client = get_client()
    address = Address(street, city, state, zipcode, country)
    card = CreditCard(card_num, exp_year, exp_month, cvn, fname, lname)
    return AuthorizeCreditCard(client, card, address=address)


def charge_card(amount, card):
    return card.capture(amount)
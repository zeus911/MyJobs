from authorize import AuthorizeInvalidError, AuthorizeResponseError
from datetime import date

from django.test import TestCase

from postajob.payment import get_card, charge_card


class PaymentTests(TestCase):
    def setUp(self):
        self.card_info = {
            'card_num': 4007000000027,
            'city': 'Indianapolis',
            'country': 'USA',
            'cvn': 123,
            'exp_month': date.today().month + 1,
            'exp_year': date.today().year + 5,
            'fname': 'John',
            'lname': 'Smith',
            'street': '123 Street Rd.',
            'state': 'Indiana',
            'zipcode': 46268,
        }

    def test_get_card(self):
        get_card(**self.card_info)

    def test_charge_card(self):
        card = get_card(**self.card_info)
        charge_card(1, card)

    def test_get_card_invalid_card(self):
        self.card_info['card_num'] = 1
        self.assertRaises(AuthorizeInvalidError, get_card,
                          **self.card_info)

    def test_get_card_invalid_exp_date(self):
        self.card_info['exp_year'] = 2013
        self.assertRaises(AuthorizeInvalidError, get_card,
                          **self.card_info)

    def test_get_card_invalid_cvn(self):
        self.card_info['cvn'] = 'a'
        self.assertRaises(AuthorizeInvalidError, get_card,
                          **self.card_info)

    # The following tests require specific triggers to be used in
    # order to get a specific error. The errors can be found at:
    # http://developer.authorize.net/tools/errorgenerationguide/
    def test_charge_card_declined(self):
        card = get_card(**self.card_info)
        self.assertRaises(AuthorizeResponseError, charge_card,
                          70.02, card)
        self.assertRaises(AuthorizeResponseError, charge_card,
                          70.03, card)
        self.assertRaises(AuthorizeResponseError, charge_card,
                          70.05, card)

    def test_charge_card_invalid_cvn(self):
        card = get_card(**self.card_info)
        self.assertRaises(AuthorizeResponseError, charge_card,
                          70.71, card)
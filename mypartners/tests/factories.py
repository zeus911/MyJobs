import factory

from mypartners.models import Partner, Contact
from myjobs.tests.models import UserFactory


class PartnerFactory(factory.Factory):
    FACTORY_FOR = Partner

    name = 'Company'
    uri = 'www.my.jobs'
    partner_of = factory.SubFactory(UserFactory)


class ContactFactory(factory.Factory):
    FACTORY_FOR = Contact

    name = 'foo bar'
    email = 'fake@email.com'
    phone = '84104391'
    address_line_one = '5683 Thing Street'

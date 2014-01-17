import factory

from mypartners.models import Partner, Contact
from mydashboard.tests.factories import CompanyFactory


class PartnerFactory(factory.Factory):
    FACTORY_FOR = Partner

    name = 'Company'
    uri = 'www.my.jobs'
    owner = factory.SubFactory(CompanyFactory)


class ContactFactory(factory.Factory):
    FACTORY_FOR = Contact

    name = 'foo bar'
    email = 'fake@email.com'
    phone = '84104391'
    address_line_one = '5683 Thing Street'

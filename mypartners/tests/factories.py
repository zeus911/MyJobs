import factory
from datetime import datetime
from django.contrib.contenttypes.models import ContentType

from mypartners.models import Partner, Contact, ContactRecord, ContactLogEntry
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


class ContactRecordFactory(factory.Factory):
    FACTORY_FOR = ContactRecord

    contact_type = 'email'
    contact_name = 'example-contact'
    contact_email = 'example@email.com'
    subject = 'Test Subject'
    notes = 'Some notes go here.'
    date_time = datetime.now()


class ContactLogEntryFactory(factory.Factory):
    FACTORY_FOR = ContactLogEntry

    action_flag = 1
    contact_identifier = "Example Contact Log"
    content_type = factory.LazyAttribute(
                       lambda a: ContentType.objects.get(name='contact'))

import factory
from factory import fuzzy
from factory import django
import string

from datetime import datetime
from django.contrib.contenttypes.models import ContentType

from mypartners.models import (Partner, Contact, ContactRecord,
                               ContactLogEntry, Tag)
from seo.tests.factories import CompanyFactory
from mydashboard.tests.factories import CompanyFactory


class PartnerFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Partner

    name = 'Company'
    uri = 'www.my.jobs'

    owner = factory.SubFactory(CompanyFactory)


class ContactFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Contact

    name = 'foo bar'
    email = 'fake@email.com'
    phone = '84104391'

    @factory.post_generation
    def locations(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for location in extracted:
                self.locations.add(location)


class ContactRecordFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ContactRecord

    contact_type = 'email'
    contact_name = 'example-contact'
    contact_email = 'example@email.com'
    subject = 'Test Subject'
    notes = 'Some notes go here.'
    date_time = datetime.now()

    partner = factory.SubFactory(PartnerFactory)


class ContactLogEntryFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ContactLogEntry

    action_flag = 1
    contact_identifier = "Example Contact Log"
    content_type = factory.LazyAttribute(
                       lambda a: ContentType.objects.get(name='contact'))


class TagFactory(factory.Factory):
    FACTORY_FOR = Tag

    name = "foo"

    company = factory.SubFactory(CompanyFactory)


class LocationFactory(django.DjangoModelFactory):
    class Meta:
        model = "mypartners.Location"

    label = "Home"
    address_line_one = factory.Sequence(lambda n: "%d Fake St" % n)
    city = fuzzy.FuzzyText()
    state = fuzzy.FuzzyText(length=2, chars=string.ascii_uppercase)
    postal_code = fuzzy.FuzzyInteger(10000, 99999)

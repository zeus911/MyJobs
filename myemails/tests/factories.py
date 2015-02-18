from factory import django, SubFactory

from django.contrib.auth.models import ContentType

from myemails import models
from seo.tests.factories import CompanyFactory


class EmailSectionHeaderFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.EmailSection

    section_type = 1
    content = 'This is a header.'


class EmailSectionBodyFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.EmailSection

    section_type = 2
    content = 'This is a body.'


class EmailSectionFooterFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.EmailSection

    section_type = 3
    content = 'This is a footer.'


class EmailTemplateFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.EmailTemplate

    header = SubFactory(EmailSectionHeaderFactory)
    body = SubFactory(EmailSectionBodyFactory)
    footer = SubFactory(EmailSectionFooterFactory)


class ValueEventFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.ValueEvent

    email_template = SubFactory(EmailTemplateFactory)
    is_active = True
    owner = SubFactory(CompanyFactory)

    model = ContentType.objects.get_for_model(models.Event)
    field = 'pk'

    compare_using = '__gte'
    value = 1


class CronEventFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.CronEvent

    email_template = SubFactory(EmailTemplateFactory)
    is_active = True
    owner = SubFactory(CompanyFactory)

    model = ContentType.objects.get_for_model(models.Event)
    field = ''

    minutes = 10
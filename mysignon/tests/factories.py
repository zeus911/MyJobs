import factory

from myjobs.tests.factories import UserFactory
from mysignon.models import AuthorizedClient


class AuthorizedClientFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = AuthorizedClient

    user = factory.SubFactory(UserFactory)
    site = 'my.jobs'

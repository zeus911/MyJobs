import factory

from myjobs.tests.factories import UserFactory

class AuthorizedClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mysignon.AuthorizedClient'

    user = factory.SubFactory(UserFactory)
    site = 'my.jobs'

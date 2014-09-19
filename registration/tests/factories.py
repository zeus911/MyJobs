import factory
from factory import fuzzy

from myjobs.tests.factories import UserFactory
from registration.models import Invitation


class InvitationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Invitation

    invitee_email = 'invitee@example.com'
    inviting_user = factory.SubFactory(
        UserFactory, email=fuzzy.FuzzyText(suffix='@example.com'))
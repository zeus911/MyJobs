import factory
from factory import fuzzy

from myjobs.tests.factories import UserFactory


class InvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        user = 'registration.Invitation'

    invitee_email = 'invitee@example.com'
    inviting_user = factory.SubFactory(
        UserFactory, email=fuzzy.FuzzyText(suffix='@example.com'))

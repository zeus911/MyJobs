import factory
import factory.django
import factory.fuzzy

from myjobs.tests.factories import UserFactory
from mymessages.models import Message, MessageInfo


class MessageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Message

    subject = factory.Sequence(lambda n: 'Subject for Message {0}'.format(n))
    body = factory.fuzzy.FuzzyText(length=30)


class MessageInfoFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = MessageInfo

    user = factory.SubFactory(UserFactory)
    message = factory.SubFactory(MessageFactory)
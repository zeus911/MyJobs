import factory
import factory.django
import factory.fuzzy

from myjobs.tests.factories import UserFactory


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mymessages.Message'

    subject = factory.Sequence(lambda n: 'Subject for Message {0}'.format(n))
    body = factory.fuzzy.FuzzyText(length=30)


class MessageInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mymessages.MessageInfo'

    user = factory.SubFactory(UserFactory)
    message = factory.SubFactory(MessageFactory)

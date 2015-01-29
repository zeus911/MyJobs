import factory
from myjobs.models import *


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myjobs.User'

    email = factory.Sequence(lambda n: 'alice%i@example.com' % n)
    gravatar = 'alice@example.com'
    password = '5UuYquA@'
    user_guid = factory.LazyAttribute(lambda n: '{0}'.format(uuid.uuid4()))
    is_active = True
    is_verified = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(create)

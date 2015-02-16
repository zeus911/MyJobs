import datetime

from django.contrib.auth.models import Group

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from myjobs.models import User
from mymessages.models import Message, MessageInfo


class MessageTests(MyJobsBase):
    def setUp(self):
        super(MessageTests, self).setUp()
        self.user = UserFactory()
        self.message = Message(subject='subject',
                               body='body',
                               message_type='success')
        self.message.save()
        for group in Group.objects.all():
            self.message.group.add(group.pk)
        self.message.save()
        self.messageInfo = MessageInfo(user=self.user,
                                       message=self.message)
        self.messageInfo.save()

    def test_message_made(self):
        m = Message.objects.all().count()
        self.assertGreaterEqual(m, 1)

    def test_message_made_sent_to_multiple(self):
        m = Message.objects.all().count()
        n_u = UserFactory(email="Best@best.com")
        n_u.groups.add(Group.objects.get(id=1).pk)
        n_u.claim_messages()
        message_info = MessageInfo.objects.all().count()
        self.assertGreaterEqual(m, 1)
        self.assertGreaterEqual(message_info, 2)

    def test_message_unread_default(self):
        m = self.messageInfo
        self.assertEqual(m.is_unread(), True)

    def test_message_read(self):
        m = self.messageInfo
        m.mark_read()
        self.assertTrue(m.read_at)

    def test_message_expired(self):
        m = self.messageInfo
        m.mark_expired()
        self.assertFalse(m.read)
        self.assertTrue(m.expired)
        self.assertTrue(m.expired_on)

    def test_message_expired_w_method(self):
        m = self.messageInfo
        m.message.expire_at = datetime.datetime.now() - \
            datetime.timedelta(days=20)
        m.message.save()
        m.expired_time()
        self.assertTrue(m.expired)

    def test_message_not_expired_w_method(self):
        m = self.messageInfo
        m.message.expire_at = datetime.datetime.now() + \
            datetime.timedelta(days=10)
        m.message.save()
        m.expired_time()
        self.assertFalse(m.expired)


class MessageManagerTests(MyJobsBase):
    def setUp(self):
        super(MessageManagerTests, self).setUp()
        self.user = UserFactory()
        self.user.groups.add(Group.objects.get(pk=1))

    def test_create_message_by_group(self):
        message = Message.objects.create_message(
            subject='subject', body='message body',
            groups=Group.objects.all())

        self.user.claim_messages()

        infos = self.user.messageinfo_set.all()
        self.assertEqual(len(infos), 1)
        self.assertEqual(infos[0].message, message)

    def test_create_message_creates_messageinfo(self):
        message = Message.objects.create_message(
            users=self.user, subject='subject', body='message body')

        infos = MessageInfo.objects.all()
        self.assertEqual(infos.count(), 1)
        self.assertEqual(infos[0].user, self.user)
        self.assertEqual(infos[0].message, message)

    def test_create_message_with_users_and_groups(self):
        new_user = UserFactory(email='second@example.com')
        message = Message.objects.create_message(
            users=new_user, subject='subject', body='message body',
            groups=Group.objects.get(pk=1))

        [user.claim_messages() for user in [new_user, self.user]]
        get_messages = lambda u: list(u.message_set.all())

        group_user_messages = get_messages(self.user)
        new_user_messages = get_messages(new_user)

        self.assertEqual(group_user_messages, new_user_messages)
        self.assertEqual(len(group_user_messages), 1)
        self.assertEqual(group_user_messages[0], message)

    def test_create_message_sets_expiration(self):
        message = Message.objects.create_message(
            subject='subject', body='message body',
            groups=Group.objects.get(pk=1), expires=False)

        self.assertTrue(message.expire_at is None)
        self.user.claim_messages()
        info = self.user.messageinfo_set.first()
        self.assertFalse(info.expired_time())

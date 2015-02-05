from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from myjobs.tests.test_views import TestClient
from mymessages.models import Message, MessageInfo
from mymessages.tests.factories import MessageInfoFactory


class MessageViewTests(MyJobsBase):
    def setUp(self):
        super(MessageViewTests, self).setUp()
        self.user = UserFactory()
        self.message = Message(subject='subject',
                               body='body',
                               message_type='success')
        self.message.save()
        for group in Group.objects.all():
            self.message.group.add(group.pk)
        self.message.save()
        self.messageinfo = MessageInfo(user=self.user,
                                       message=self.message)
        self.messageinfo.save()
        self.client = TestClient()
        self.client.login_user(self.user)

    def test_user_post_mark_message_read(self):
        self.client.get(reverse('read'),
                        data={'name': 'message-read-'+str(self.message.id)
                                      + '-'+str(self.user.id)},
                        follow=True,
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        m = MessageInfo.objects.get(user=self.user, message=self.message)
        self.assertTrue(m.read)
        self.assertTrue(m.read_at)

    def test_delete_message_single_recipient(self):
        """
        Deleting a MessageInfo when there is only one recipient also deletes
        the message associated with it.
        """
        self.client.get(reverse('delete'),
                        data={'name': 'message-delete-'+str(self.message.id)
                                      + '-'+str(self.user.id)},
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        with self.assertRaises(MessageInfo.DoesNotExist):
            MessageInfo.objects.get(pk=self.messageinfo.pk)
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=self.message.pk)

    def test_delete_message_multiple_recipients(self):
        """
        Deleting a MessageInfo with multiple recipients deletes the info for
        the current user only.
        """
        user = UserFactory(email='new@example.com')
        messageinfo = MessageInfo.objects.create(user=user, message=self.message)

        self.client.get(reverse('delete'),
                        data={'name': 'message-delete-'+str(self.message.id)
                                      + '-'+str(self.user.id)},
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        with self.assertRaises(MessageInfo.DoesNotExist):
            MessageInfo.objects.get(pk=self.messageinfo.pk)
        Message.objects.get(pk=self.message.pk)
        MessageInfo.objects.get(pk=messageinfo.pk)

    def test_auto_page_inbox(self):
        infos = MessageInfoFactory.create_batch(11, user=self.user)
        request = self.client.get(reverse('inbox'))
        self.assertTrue('Page 1 of 2' in request.content)

        request = self.client.get(reverse('inbox') +
                                  '?message=%s' % infos[-1].message.pk)
        self.assertTrue('Page 2 of 2' in request.content)

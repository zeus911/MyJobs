import datetime

from django.utils.unittest.case import TestCase

from myjobs.models import STOP_SENDING, BAD_EMAIL, EmailLog, User
from myjobs.tests.factories import UserFactory
from tasks import process_batch_events


class TaskTests(TestCase):
    def test_bad_events_deactivate_user(self):
        now = datetime.datetime.now()
        for event in STOP_SENDING + BAD_EMAIL:
            u = UserFactory(is_verified=True, opt_in_myjobs=True)
            EmailLog.objects.create(email=u.email, event=event, received=now,
                                    processed=False)
            process_batch_events()

            u = User.objects.get(pk=u.pk)
            self.assertEqual(u.deactivate_type, event)
            self.assertFalse(u.is_verified)
            self.assertFalse(u.opt_in_myjobs)

            infos = u.messages_unread()
            self.assertEqual(len(infos), 1)
            message = infos[0].message

            if u.deactivate_type in STOP_SENDING:
                text = 'stop communications'
            else:
                text = 'Attempts to send messages to'
            self.assertTrue(text in message.body)

            EmailLog.objects.all().delete()
            u.delete()

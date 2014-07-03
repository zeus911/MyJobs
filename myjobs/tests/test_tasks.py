import datetime

from django.utils.unittest.case import TestCase

from myjobs.models import DEACTIVE_TYPES, EmailLog, User
from myjobs.tests.factories import UserFactory
from tasks import process_batch_events


class TaskTests(TestCase):
    def test_bad_events_deactivate_user(self):
        now = datetime.datetime.now()
        for event in DEACTIVE_TYPES:
            u = UserFactory()
            EmailLog.objects.create(email=u.email, event=event, received=now,
                                    processed=False)
            process_batch_events()

            u = User.objects.get(pk=u.pk)
            self.assertEqual(u.deactive_type, event)
            self.assertFalse(u.is_active)
            self.assertFalse(u.opt_in_myjobs)

            EmailLog.objects.all().delete()
            u.delete()

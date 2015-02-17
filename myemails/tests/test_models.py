from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType

from myemails.tests import factories
from myjobs.tests.setup import MyJobsBase
from mysearches.tests.factories import SavedSearchFactory


class EmailTemplateTests(MyJobsBase):
    def test_build_context(self):
        pass

    def test_email_template_render(self):
        email_template = factories.EmailTemplateFactory()
        # TODO: Update to actually use for_object and context.
        rendered_email = email_template.render(email_template)

        # Default email content comes from the
        default_email = 'This is a header.\nThis is a body.\nThis is a footer.'
        self.assertEqual(rendered_email, default_email)


class EventTests(MyJobsBase):
    def test_event_send_email(self):
        pass


class CronEventTests(MyJobsBase):
    def setUp(self):
        super(CronEventTests, self).setUp()
        # I'm using SavedSearch for these tests, but you can use any
        # model with a DateTimeField for the "*_with_field" option, and
        # any object for the "*_no_field" option.
        # It might actually be worth using additional object types
        # in future tests.
        yesterday = datetime.now() - timedelta(1)
        self.saved_search = SavedSearchFactory(last_sent=yesterday)

        model = self.saved_search._meta.model
        self.saved_search_contenttype = ContentType.objects.get_for_model(model)
        cron_kwargs = {'model': self.saved_search_contenttype}
        self.cron_event_no_field = factories.CronEventFactory(**cron_kwargs)
        cron_kwargs['field'] = 'last_sent'
        self.cron_event_with_field = factories.CronEventFactory(**cron_kwargs)

    def test_cron_event_schedule_task_no_field(self):
        today = datetime.now().date()
        task = self.cron_event_no_field.schedule_task(self.saved_search)

        self.assertEqual(task.object_id, self.saved_search.id)
        self.assertEqual(task.model, self.saved_search_contenttype)
        self.assertEqual(task.related_event, self.cron_event_no_field)
        self.assertEqual(task.scheduled_for.date(), today)
        self.assertEqual(task.scheduled_at.date(), today)
        self.assertIsNone(task.completed_on)

    def test_cron_event_schedule_task_with_field(self):
        yesterday = (datetime.now() - timedelta(1)).date()
        today = datetime.now().date()
        task = self.cron_event_with_field.schedule_task(self.saved_search)

        self.assertEqual(task.object_id, self.saved_search.id)
        self.assertEqual(task.model, self.saved_search_contenttype)
        self.assertEqual(task.related_event, self.cron_event_with_field)
        self.assertEqual(task.scheduled_for.date(), yesterday)
        self.assertEqual(task.scheduled_at.date(), today)
        self.assertIsNone(task.completed_on)

    def test_scheduled_for_with_field(self):
        """
        CronEvents that have an associated field should schedule from the
        time contained within the associated field.
        
        """
        tomorrow = datetime.now() + timedelta(1)
        self.saved_search.last_sent = tomorrow
        self.saved_search.save()

        self.cron_event_with_field.minutes = 60*25
        self.cron_event_with_field.save()
        should_be_scheduled_for = (tomorrow + timedelta(1)).date()

        task = self.cron_event_with_field.schedule_task(self.saved_search)
        self.assertEqual(task.scheduled_for.date(), should_be_scheduled_for)

    def test_scheduled_for_no_field(self):
        """
        CronEvents that don't have an associated field should instead be
        scheduled based on the current time.

        """
        self.cron_event_no_field.minutes = 60
        self.cron_event_no_field.save()
        should_be_scheduled_for = datetime.now() + timedelta(minutes=60)
        should_be_scheduled_for = should_be_scheduled_for.date()

        task = self.cron_event_no_field.schedule_task(self.saved_search)
        self.assertEqual(task.scheduled_for.date(), should_be_scheduled_for)
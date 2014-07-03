import datetime
from mock import patch
from StringIO import StringIO

from django.test import TestCase

from mydashboard.tests.factories import CompanyFactory
from myjobs.models import DEACTIVE_TYPES_AND_NONE, DEACTIVE_TYPES, EmailLog, \
    User
from myjobs.tests.factories import UserFactory
from postajob.models import Job
from tasks import expire_jobs, process_batch_events


class TaskTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.job_data = {
            'title': 'title',
            'company': self.company,
            'description': 'sadfljasdfljasdflasdfj',
            'apply_link': 'www.google.com',
            'city': 'Indianapolis',
            'state': 'Indiana',
            'state_short': 'IN',
            'country': 'United States of America',
            'country_short': 'USA',
            'zipcode': '46268',
        }

    @patch('urllib2.urlopen')
    def test_expire_jobs(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        # Jobs with expiration dates in the past and future should not get
        # expired.
        for x in range(0, 5):
            job = dict(self.job_data)
            job['date_new'] = datetime.datetime.now()
            job['date_updated'] = datetime.datetime.now()
            job['date_expired'] = datetime.date.today() + datetime.timedelta(days=-5)
            job['guid'] = ('%s' % x)*32
            Job.objects.create(**job)
        self.assertEqual(Job.objects.all().count(), 5)
        # add_to_solr() should've called urlopen once for each job.
        self.assertEqual(urlopen_mock.call_count, 5)
        for x in range(5, 10):
            job = dict(self.job_data)
            job['date_new'] = datetime.datetime.now()
            job['date_updated'] = datetime.datetime.now()
            job['date_expired'] = datetime.date.today() + datetime.timedelta(days=-5)
            job['guid'] = ('%s' % x)*32
            Job.objects.create(**job)
        self.assertEqual(Job.objects.all().count(), 10)
        self.assertEqual(urlopen_mock.call_count, 10)
        # Only jobs that expire today should be expired in the next
        # expire_jobs() call.
        for x in range(10, 15):
            job = dict(self.job_data)
            job['date_new'] = datetime.datetime.now()
            job['date_updated'] = datetime.datetime.now()
            job['date_expired'] = datetime.date.today()
            job['guid'] = ('%s' % x)*32
            Job.objects.create(**job)
        self.assertEqual(Job.objects.all().count(), 15)
        self.assertEqual(urlopen_mock.call_count, 15)

        expire_jobs()
        # remove_from_solr() should've called urlopen one time
        # for each newly expired job.
        self.assertEqual(urlopen_mock.call_count, 20)
        self.assertEqual(Job.objects.filter(is_expired=True).count(), 5)
        self.assertEqual(Job.objects.filter(is_expired=False).count(), 10)

    @patch('urllib2.urlopen')
    def test_expire_jobs_with_autorenew(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        for x in range(0, 5):
            job = dict(self.job_data)
            job['date_new'] = datetime.datetime.now()
            job['date_updated'] = datetime.datetime.now()
            job['date_expired'] = datetime.date.today() + datetime.timedelta(days=-5)
            job['guid'] = ('%s' % x)*32
            Job.objects.create(**job)
        self.assertEqual(Job.objects.all().count(), 5)
        self.assertEqual(urlopen_mock.call_count, 5)
        for x in range(5, 10):
            job = dict(self.job_data)
            job['date_new'] = datetime.datetime.now()
            job['date_updated'] = datetime.datetime.now()
            job['date_expired'] = datetime.date.today()
            job['guid'] = ('%s' % x)*32
            Job.objects.create(**job)
        self.assertEqual(Job.objects.all().count(), 10)
        self.assertEqual(urlopen_mock.call_count, 10)
        for x in range(10, 15):
            job = dict(self.job_data)
            job['date_new'] = datetime.datetime.now()
            job['date_updated'] = datetime.datetime.now()
            job['date_expired'] = datetime.date.today()
            job['guid'] = ('%s' % x)*32
            job['autorenew'] = True
            Job.objects.create(**job)
        self.assertEqual(Job.objects.all().count(), 15)
        self.assertEqual(urlopen_mock.call_count, 15)

        expire_jobs()

        autorenew_jobs = Job.objects.filter(autorenew=True, is_expired=False)
        new_expire_date = datetime.date.today() + datetime.timedelta(days=30)
        self.assertEqual(autorenew_jobs.count(), 5)

        # No jobs should've accidently been marked as autorenew that weren't
        # autorenew jobs.
        self.assertEqual(Job.objects.filter(is_expired=True).count(), 5)
        self.assertEqual(Job.objects.filter(is_expired=False,
                                            autorenew=False).count(), 5)

        # date_expired should've been moved up one month for expired autorenew
        # jobs.
        for job in autorenew_jobs:
            self.assertEqual(new_expire_date, job.date_expired)

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

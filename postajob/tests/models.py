import datetime
from mock import patch
from StringIO import StringIO
from urlparse import parse_qs

from django.conf import settings
from django.test import TestCase

from mydashboard.tests.factories import CompanyFactory, SeoSiteFactory
from postajob.models import Job


class ModelTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.site = SeoSiteFactory()
        self.job_data = {
            'title': 'title',
            'company': self.company,
            'reqid': '1',
            'description': 'sadfljasdfljasdflasdfj',
            'apply_link': 'www.google.com',
            'city': 'Indianapolis',
            'state': 'Indiana',
            'state_short': 'IN',
            'country': 'United States of America',
            'country_short': 'USA',
            'zipcode': '46268',
            'date_new': datetime.datetime.now(),
            'date_updated': datetime.datetime.now(),
            'date_expired': datetime.date.today(),
            'guid': 'abcdef123456',
        }
        self.request_data = {
            'title': 'title',
            'company': self.company.id,
            'reqid': '1',
            'description': 'sadfljasdfljasdflasdfj',
            'link': 'www.google.com',
            'city': 'Indianapolis',
            'state': 'Indiana',
            'state_short': 'IN',
            'country': 'United States of America',
            'country_short': 'USA',
            'zipcode': '46268',
            'guid': 'abcdef123456',
            'on_sites': '',
            'apply_info': '',
        }

    @patch('urllib2.urlopen')
    def test_job_creation(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_added": 1}')
        Job.objects.create(**self.job_data)
        self.assertEqual(Job.objects.all().count(), 1)

    @patch('urllib2.urlopen')
    def test_job_deletion(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_deleted": 1}')
        job = Job.objects.create(**self.job_data)
        self.assertEqual(Job.objects.all().count(), 1)
        job.delete()
        self.assertEqual(Job.objects.all().count(), 0)

    @patch('urllib2.urlopen')
    def test_add_to_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_added": 1}')
        Job.objects.create(**self.job_data)
        # add_to_solr() is called in save(), so urlopen should've been
        # called once at this point.
        self.assertEqual(urlopen_mock.call_count, 1)

        # Determine what is being sent to microsites by parsing the
        # Request object passed to urlopen().
        args, _ = urlopen_mock.call_args
        data = parse_qs(args[0].data)
        data['jobs'] = eval(data['jobs'][0])
        self.assertEqual(data['key'][0], settings.POSTAJOB_API_KEY)
        for field in self.request_data.keys():
            self.assertEqual(data['jobs'][0][field], self.request_data[field])

    @patch('urllib2.urlopen')
    def test_remove_from_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_deleted": 1}')
        job = Job.objects.create(**self.job_data)
        job.remove_from_solr()

        # add_to_solr() is called in save(), which is combined with the
        # call to remove_from_solr().
        self.assertEqual(urlopen_mock.call_count, 2)

        # Determine what is being sent to microsites by parsing the
        # Request object passed to urlopen().
        args, _ = urlopen_mock.call_args
        data = parse_qs(args[0].data)
        self.assertEqual(data['key'][0], settings.POSTAJOB_API_KEY)
        self.assertEqual(data['guids'][0], self.request_data['guid'])

    @patch('urllib2.urlopen')
    def test_generate_guid(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')

        # Confirm that pre-assigned guids are not being overwritten.
        job = Job.objects.create(**self.job_data)
        self.assertEqual(self.job_data['guid'], job.guid)
        job.delete()

        # Confirm that if a guid isn't assigned one is getting assigned
        # to it properly.
        guid = self.job_data['guid']
        del self.job_data['guid']
        job = Job.objects.create(**self.job_data)
        self.assertIsNotNone(job.guid)
        self.assertNotEqual(job.guid, guid)

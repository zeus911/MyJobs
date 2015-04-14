import os
import pysolr

from django.conf import settings
from django.test import TestCase

from api.import_jobs import clear_solr, import_from_file
from api.tests.factories import APIUserFactory


class BaseTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        super(BaseTestCase, self).setUp()
        settings.SOLR_LOCATION = settings.TESTING_SOLR_LOCATION
        self.solr = pysolr.Solr(settings.SOLR_LOCATION)
        self.user = APIUserFactory()
        self.path = '/?key=%s&' % self.user.key
        self.countspath = '/countsapi.asp?key=%s&' % self.user.key
        self.search_mapping = {'onet': '12345678', 'tm': '10',
                               'ind': '1', 'cn': '100', 'zc': '12345',
                               'zc1': '12345', 'rd1': '1000',
                               'cname': 'acme', 'i': 's', 'moc': 'mmmm',
                               'branch': 'army', 'so': 'initdate',
                               'rs': '4', 're': '23', 'si': '1', }

        # Job-specific information from dseo_feed_1.xml
        self.fixture_jvid = '0F21D879F4904BDB90EC27A3843A1B0910'
        self.fixture_onets = '12345678'

        testdir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'data')
        feed = os.path.join(testdir, 'dseo_feed_1.xml')
        import_from_file(feed, testing=True)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        clear_solr()
        self.assertEqual(self.solr.search('*:*').hits, 0)
import pysolr

from django.conf import settings
from django.core.urlresolvers import clear_url_caches
from django.test import TransactionTestCase

from api.tests.data.job_data import JOBS
from api.tests.factories import APIUserFactory


class APIBaseTestCase(TransactionTestCase):
    fixtures = ['test_data.json']
    multi_db = True

    def setUp(self):
        super(APIBaseTestCase, self).setUp()
        setattr(settings, 'ROOT_URLCONF', 'api_urls')
        setattr(settings, "PROJECT", 'api')
        clear_url_caches()

        settings.SOLR_LOCATION = 'http://127.0.0.1:8983/solr/api_test'
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

        self.solr.add(JOBS)
        self.assertEqual(self.solr.search('*:*').hits, 2)

    def tearDown(self):
        super(APIBaseTestCase, self).tearDown()
        self.solr.delete(q='*:*')
        self.assertEqual(self.solr.search('*:*').hits, 0)
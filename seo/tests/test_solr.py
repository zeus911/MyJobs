from django.conf import settings
from django.core.urlresolvers import reverse

from seo.models import SeoSite
from seo.tests import factories
from seo.tests.solr_settings import SOLR_FIXTURE
from setup import DirectSEOTestCase
from universal.helpers import build_url


class QueryCountTests(DirectSEOTestCase):
    def setUp(self):
        super(QueryCountTests, self).setUp()
        settings.SOLR_QUERY_COUNTER = 0

        # For each search page there should be at least 2 queries:
        #   default jobs, total jobs
        # There can also be an additional two queries:
        #   featured jobs, custom facets
        # For a total of at least 2 queries but at most 4
        self.query_range = range(2, 4+1)

        # Make a valid non-dns-homepage configuration to use.
        site = SeoSite.objects.get(domain='secure.my.jobs')
        site.configurations.all().delete()
        site.configurations.add(factories.ConfigurationFactory(status=2))
        site.business_units.add(0)

        # Insert extra jobs so we know the search pages
        # aren't iterating through all jobs for some reason.
        bulk_jobs = []
        job = SOLR_FIXTURE[0]
        for i in range(5000, 5050):
            guid = str(i)*8
            new_job = dict(job)
            new_job['guid'] = guid
            new_job['uid'] = new_job['id'] = new_job['django_id'] = i
            bulk_jobs.append(new_job)
        self.conn.add(bulk_jobs)
        # Make sure there's not an id collision and we're really adding
        # all the jobs we think we just added.
        self.assertGreaterEqual(self.conn.search(q='*:*').hits, len(bulk_jobs))

        # Two search terms that are guaranteed to yield results
        # including all the new jobs we just inserted.
        self.location = 'Indianapolis'
        self.q = 'description'

        self.path = '/usa/jobs/'
        self.feed_types = ['json', 'rss', 'xml', 'atom', 'indeed', 'jsonp']

    def tearDown(self):
        settings.SOLR_QUERY_COUNTER = 0
        super(QueryCountTests, self).tearDown()

    def test_num_queries_homepage(self):
        self.client.get(reverse('home'))
        self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)

    def test_num_queries_search_results(self):
        self.client.get(reverse('all_jobs'))
        self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)

    def test_num_queries_search_results_with_path(self):
        self.client.get(self.path)
        self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)

    def test_num_queries_search_results_with_querystring(self):
        path = reverse('all_jobs')
        self.client.get(build_url(path, {'location': self.location}))
        self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)

    def test_num_queries_search_results_with_path_and_querystring(self):
        self.client.get(build_url(self.path, {'q': self.q}))
        self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)

    def test_feed(self):
        for feed_type in self.feed_types:
            kwargs = {
                'feed_type': feed_type,
                'filter_path': reverse('all_jobs')
            }
            self.client.get(reverse('feed', kwargs=kwargs))
            self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)
            settings.SOLR_QUERY_COUNTER = 0

    def test_feed_with_path(self):
        for feed_type in self.feed_types:
            kwargs = {
                'feed_type': feed_type,
                'filter_path': self.path
            }
            self.client.get(reverse('feed', kwargs=kwargs))
            self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)
            settings.SOLR_QUERY_COUNTER = 0

    def test_feed_with_querystring(self):
        for feed_type in self.feed_types:
            kwargs = {
                'feed_type': feed_type,
                'filter_path': reverse('all_jobs')
            }
            path = reverse('feed', kwargs=kwargs)
            self.client.get(build_url(path, {'location': self.location}))
            self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)
            settings.SOLR_QUERY_COUNTER = 0

    def test_feed_with_path_and_querystring(self):
        for feed_type in self.feed_types:
            kwargs = {
                'feed_type': feed_type,
                'filter_path': self.path
            }
            path = reverse('feed', kwargs=kwargs)
            self.client.get(build_url(path, {'q': self.q}))
            self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)
            settings.SOLR_QUERY_COUNTER = 0

    def test_job_detail_page(self):
        guid = SOLR_FIXTURE[1]['guid']
        title = SOLR_FIXTURE[1]['title_exact']
        url = reverse('job_detail_by_job_id', kwargs={'job_id': guid})
        resp = self.client.get(url, follow=True)
        self.assertIn(settings.SOLR_QUERY_COUNTER, self.query_range)

        # Confirm we've actually reached a description page
        # by checking for the title in the response.
        self.assertIn(title, resp.content)
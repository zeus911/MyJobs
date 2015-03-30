from django.conf import settings
from django.core.urlresolvers import reverse

from myblocks import context_tools
from myblocks.tests.setup import BlocksTestBase


class ContextToolsTests(BlocksTestBase):
    """
    Really basic tests to make sure that the context_tools function.
    More in-depth tests will are on the helper functions used by
    the context tools.

    """
    def test_get_arranged_jobs(self):
        arranged_jobs = context_tools.get_arranged_jobs(self.search_results_request)

        for job_dict in arranged_jobs:
            if job_dict['class'] == 'default_jobListing':
                self.assertEqual(len(job_dict['jobs']), 1)
            else:
                self.assertEqual(len(job_dict['jobs']), 0)

    def test_get_breadbox(self):
        breadbox = context_tools.get_breadbox(self.search_results_request)
        self.assertEqual(breadbox.path, reverse('all_jobs'))
        self.assertEqual(breadbox.job_count, '1')
        self.assertIsNone(breadbox.q_breadcrumb)

        breadbox = context_tools.get_breadbox(self.search_results_with_q_request)
        self.assertEqual(breadbox.path, reverse('all_jobs'))
        self.assertEqual(breadbox.job_count, '1')
        self.assertEqual(breadbox.q_breadcrumb.display_title, self.job['title'])

    def test_get_custom_facet_counts(self):
        custom_facet_counts = context_tools.get_custom_facet_counts(self.search_results_request)
        self.assertGreaterEqual(len(custom_facet_counts), 1)
        for facet, count in custom_facet_counts:
            if facet.always_show:
                self.assertGreaterEqual(count, 0)
            else:
                self.assertGreater(count, 0)

    def test_get_default_jobs(self):
        jobs = context_tools.get_default_jobs(self.search_results_request)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].guid, self.job['guid'])

    def test_get_facet_blurb_facet(self):
        facet = context_tools.get_facet_blurb_facet(self.search_results_with_custom_facet)
        self.assertEqual(facet.blurb, self.facet.blurb)

    def test_get_featured_jobs(self):
        jobs = context_tools.get_featured_jobs(self.search_results_request)
        self.assertEqual(len(jobs), 0)

        settings.FEATURED_FACET = [self.facet]
        jobs = context_tools.get_featured_jobs(self.search_results_request)
        self.assertEqual(len(jobs), 1)

    def test_get_job_detail_breadbox(self):
        breadbox = context_tools.get_job_detail_breadbox(self.job_detail_request,
                                                         self.job['guid'])
        self.assertEqual(breadbox['city']['display'], self.job['city'])
        self.assertEqual(breadbox['state']['display'], self.job['state'])
        self.assertEqual(breadbox['country']['display'], self.job['country'])
        self.assertEqual(breadbox['title']['display'], self.job['title'])

    def test_get_location_term(self):
        # Location term should come from the job on the job detail page
        location_term = context_tools.get_location_term(self.job_detail_request,
                                                        **self.job_detail_kwargs)
        self.assertEqual(self.job['location'], location_term)

        location_term = context_tools.get_location_term(self.search_results_request)
        self.assertEqual(location_term, '')

    def test_get_site_commitments_string(self):
        string = context_tools.get_site_commitments_string(self.search_results_request)
        self.assertEqual(string, self.commitment.commit)
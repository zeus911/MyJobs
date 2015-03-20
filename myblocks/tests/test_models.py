from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from myblocks import models
from myblocks.tests import factories
from myjobs.tests.factories import UserFactory
from seo.models import Configuration, SeoSite, SiteTag
from seo.tests.factories import (CustomFacetFactory, SeoSiteFactory,
                                 SeoSiteFacetFactory, SpecialCommitmentFactory)
from seo.tests.setup import DirectSEOBase
from seo.tests.solr_settings import SOLR_FIXTURE
from universal.helpers import build_url


class ModelsTests(DirectSEOBase):
    def setUp(self):
        super(ModelsTests, self).setUp()
        self.site = SeoSite.objects.get()
        self.config = Configuration.objects.get(status=2)
        self.config.browse_facet_show = True
        self.config.save()

        self.commitment = SpecialCommitmentFactory()
        self.site.special_commitments.add(self.commitment)
        self.site.save()

        self.tag = SiteTag.objects.create(site_tag='Test tag')
        self.site.site_tags.add(self.tag)
        self.site.save()

        self.job = SOLR_FIXTURE[1]
        self.conn.add([self.job])

        user = UserFactory()

        url = reverse('all_jobs')
        self.search_results_request = RequestFactory().get(url)
        self.search_results_request.user = user

        url = build_url(reverse('all_jobs'), {'q': 'Retail'})
        self.search_results_with_q_request = RequestFactory().get(url)
        self.search_results_with_q_request.user = user

        self.facet = CustomFacetFactory(show_production=True,
                                        name='Retail',
                                        name_slug='retail',
                                        querystring='Retail',
                                        blurb='Test')
        SeoSiteFacetFactory(customfacet=self.facet, seosite=self.site)
        url = 'retail/new-jobs/'
        self.search_results_with_custom_facet = RequestFactory().get(url)
        self.search_results_with_custom_facet.user = user

        kwargs = {'job_id': self.job['guid']}
        url = reverse('job_detail_by_job_id', kwargs=kwargs)
        self.job_detail_request = RequestFactory().get(url)
        self.job_detail_request.user = user

        # Send a request through middleware so all the required
        # settings (from MultiHostMiddleware) actually get set.
        self.client.get('/')

    def test_block_bootstrap_classes(self):
        block = factories.BlockFactory(offset=5, span=3)
        block2 = factories.BlockFactory(offset=3, span=7)

        self.assertEqual(block.bootstrap_classes(),
                         'col-md-offset-5 col-md-3')
        self.assertEqual(block2.bootstrap_classes(),
                         'col-md-offset-3 col-md-7')

    def test_block_cast(self):
        models.Block.objects.all().delete()
        factories.LoginBlockFactory()
        block = models.Block.objects.get()
        self.assertIsInstance(block, models.Block)
        self.assertIsInstance(block.cast(), models.LoginBlock)

    def test_apply_link_context(self):
        apply_link_block = factories.ApplyLinkBlockFactory()

        # The job that is returned for the apply link url should match
        # the one requested.
        context = apply_link_block.context(self.job_detail_request,
                                           job_id=self.job['guid'])
        self.assertEqual(context['apply_link_job'].guid, self.job['guid'])

        # When there isn't actually a job being requested we shouldn't
        # get a job populating the apply link field.
        context = apply_link_block.context(self.job_detail_request)
        self.assertIsNone(context['apply_link_job'])

    def test_breadbox_context(self):
        breadbox_block = factories.BreadboxBlockFactory()

        context = breadbox_block.context(self.search_results_request)
        breadbox = context['breadbox']

        self.assertEqual(breadbox.path, reverse('all_jobs'))
        self.assertEqual(breadbox.job_count, '1')
        self.assertIsNone(breadbox.q_breadcrumb)

        context = breadbox_block.context(self.search_results_with_q_request)
        breadbox = context['breadbox']
        self.assertEqual(breadbox.path, reverse('all_jobs'))
        self.assertEqual(breadbox.job_count, '1')
        self.assertEqual(breadbox.q_breadcrumb.display_title, 'Retail')

    def test_column_block_context(self):
        column_block = factories.ColumnBlockFactory()
        search_filter_block = factories.SearchFilterBlockFactory()
        breadbox_block = factories.BreadboxBlockFactory()

        models.ColumnBlockOrder.objects.create(block=search_filter_block,
                                               column_block=column_block,
                                               order=1)
        models.ColumnBlockOrder.objects.create(block=breadbox_block,
                                               column_block=column_block,
                                               order=2)

        context = column_block.context(self.search_results_request)
        keys = context.keys()

        # The context shiould contain the required context for both
        # blocks.
        expected_context = ['widgets', 'breadbox']
        for field in expected_context:
            self.assertIn(field, keys)
            self.assertIsNotNone(context[field])

    def test_column_block_template(self):
        one = 'template one'
        two = 'template two'

        column_block = factories.ColumnBlockFactory()
        search_filter_block = factories.SearchFilterBlockFactory(template=one)
        breadbox_block = factories.BreadboxBlockFactory(template=two)

        models.ColumnBlockOrder.objects.create(block=search_filter_block,
                                               column_block=column_block,
                                               order=1)
        models.ColumnBlockOrder.objects.create(block=breadbox_block,
                                               column_block=column_block,
                                               order=2)

        # Confirm that both templates are joined together in the correct order
        template = column_block.get_template()
        self.assertRegexpMatches(template, '.*%s.*%s.*' % (one, two))

        # Try a new order.
        reverse_column_block = factories.ColumnBlockFactory()
        models.ColumnBlockOrder.objects.create(block=search_filter_block,
                                               column_block=reverse_column_block,
                                               order=2)
        models.ColumnBlockOrder.objects.create(block=breadbox_block,
                                               column_block=reverse_column_block,
                                               order=1)

        # Confirm that both templates are again joined in the correct order.
        template = reverse_column_block.get_template()
        self.assertRegexpMatches(template, '.*%s.*%s.*' % (two, one))

    def test_column_block_required_js(self):
        column_block = factories.ColumnBlockFactory()
        search_filter_block = factories.SearchFilterBlockFactory()
        breadbox_block = factories.BreadboxBlockFactory()

        models.ColumnBlockOrder.objects.create(block=search_filter_block,
                                               column_block=column_block,
                                               order=1)
        models.ColumnBlockOrder.objects.create(block=breadbox_block,
                                               column_block=column_block,
                                               order=2)
        models.ColumnBlockOrder.objects.create(block=search_filter_block,
                                               column_block=column_block,
                                               order=3)

        js = column_block.required_js()

        # Only SearchFilterBlock has expected js, and that js should be
        # included only once.
        search_filter_block_js = search_filter_block.required_js()
        self.assertEqual(len(js), len(search_filter_block_js))
        self.assertEqual(search_filter_block_js, js)

    def test_facet_blurb_context(self):
        facet_blurb_block = factories.FacetBlurbBlockFactory()

        # Pages with no custom facets applied should not have a
        # facet_blurb_facet.
        context = facet_blurb_block.context(self.search_results_request)
        self.assertIsNone(context['facet_blurb_facet'])

        # Pages with custom facets that have a facet blurb should
        # have a facet_blurb_facet.
        context = facet_blurb_block.context(self.search_results_with_custom_facet)
        self.assertIsNotNone(context['facet_blurb_facet'])

    def test_job_detail_context(self):
        job_detail_block = factories.JobDetailBlockFacetory()

        context = job_detail_block.context(self.job_detail_request,
                                           job_id=self.job['guid'])
        self.assertEqual(context['requested_job'].guid, self.job['guid'])
        self.assertEqual(context['site_commitments_string'],
                         self.commitment.commit)

        # When there isn't actually a job we shouldn't get a job
        # but we should still get a site_commitments_string.
        context = job_detail_block.context(self.job_detail_request)
        self.assertIsNone(context['requested_job'])
        self.assertEqual(context['site_commitments_string'],
                         self.commitment.commit)

    def test_job_detail_breadbox_context(self):
        job_detail_breadbox_block = factories.JobDetailBreadboxBlockFactory()

        context = job_detail_breadbox_block.context(self.job_detail_request,
                                                    job_id=self.job['guid'])
        breadcrumbs = context['job_detail_breadcrumbs']
        self.assertEqual(breadcrumbs['city']['display'], self.job['city'])
        self.assertEqual(breadcrumbs['state']['display'], self.job['state'])
        self.assertEqual(breadcrumbs['country']['display'], self.job['country'])
        self.assertEqual(breadcrumbs['title']['display'], self.job['title'])

    def test_job_detail_header_context(self):
        job_detail_header_block = factories.JobDetailHeaderBlockFactory()

        context = job_detail_header_block.context(self.job_detail_request,
                                                  job_id=self.job['guid'])
        self.assertEqual(context['requested_job'].guid, self.job['guid'])

    def test_more_button_context(self):
        more_button_block = factories.MoreButtonBlockFactory()

        context = more_button_block.context(self.search_results_request)
        self.assertIsNotNone(context['arranged_jobs'])
        self.assertEqual(context['num_default_jobs'], 1)
        self.assertEqual(context['num_featured_jobs'], 0)
        self.assertEqual(context['site_config'], self.config)

    def test_search_box_context(self):
        search_box_block = factories.SearchBoxBlockFactory()

        # Job Detail location_term should be the job's location.
        context = search_box_block.context(self.job_detail_request,
                                           job_id=self.job['guid'])
        self.assertEqual(context['search_url'], self.job_detail_request.path)
        self.assertEqual(context['moc_id_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['title_term'], '')
        self.assertEqual(context['location_term'], self.job['location'])
        self.assertEqual(context['site_config'], self.config)

        context = search_box_block.context(self.search_results_request)
        path = self.search_results_request.path
        self.assertEqual(context['search_url'], path)
        self.assertEqual(context['moc_id_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['title_term'], '')
        self.assertEqual(context['location_term'], '')
        self.assertEqual(context['site_config'], self.config)

        # Search box should inherit search terms.
        context = search_box_block.context(self.search_results_with_q_request)
        path = self.search_results_with_q_request.path
        q_term = self.search_results_with_q_request.GET['q']
        self.assertEqual(context['search_url'], path)
        self.assertEqual(context['moc_id_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['title_term'], q_term)
        self.assertEqual(context['location_term'], '')
        self.assertEqual(context['site_config'], self.config)

    def test_search_filter_context(self):
        search_filter_block = factories.SearchFilterBlockFactory()

        context = search_filter_block.context(self.search_results_request)
        self.assertIsNotNone(context['widgets'])

    def test_search_result_context(self):
        search_result_block = factories.SearchResultFactory()

        context = search_result_block.context(self.search_results_request)
        self.assertIsNotNone(context['arranged_jobs'])
        self.assertEqual(len(context['default_jobs']), 1)
        self.assertEqual(len(context['featured_jobs']), 0)
        self.assertEqual(context['location_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['query_string'], '')
        self.assertNotEqual(context['results_heading'], '')
        self.assertEqual(context['site_commitments_string'],
                         self.commitment.commit)
        self.assertEqual(context['site_config'], self.config)
        self.assertEqual(context['site_tags'], [self.tag.site_tag])
        self.assertEqual(context['title_term'], '')

        context = search_result_block.context(self.search_results_with_q_request)
        q_term = self.search_results_with_q_request.GET['q']
        self.assertEqual(context['query_string'], 'q=%s' % q_term)
        self.assertEqual(context['title_term'], q_term)

    def test_search_result_header_context(self):
        search_result_header_block = factories.SearchResultHeaderFactory()

        context = search_result_header_block.context(self.search_results_request)
        self.assertIsNotNone(context['arranged_jobs'])
        self.assertNotEqual(context['count_heading'], '')
        self.assertEqual(len(context['default_jobs']), 1)
        self.assertEqual(len(context['featured_jobs']), 0)
        self.assertEqual(context['location_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['query_string'], '')
        self.assertEqual(context['title_term'], '')

        context = search_result_header_block.context(self.search_results_with_q_request)
        q_term = self.search_results_with_q_request.GET['q']
        self.assertEqual(context['query_string'], 'q=%s' % q_term)
        self.assertEqual(context['title_term'], q_term)

    def test_veteran_search_box_context(self):
        veteran_search_box_block = factories.VeteranSearchBoxBlockFactory()

        # Job Detail location_term should be the job's location.
        context = veteran_search_box_block.context(self.job_detail_request,
                                                   job_id=self.job['guid'])
        self.assertEqual(context['search_url'], self.job_detail_request.path)
        self.assertEqual(context['moc_id_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['title_term'], '')
        self.assertEqual(context['location_term'], self.job['location'])
        self.assertEqual(context['site_config'], self.config)

        context = veteran_search_box_block.context(self.search_results_request)
        path = self.search_results_request.path
        self.assertEqual(context['search_url'], path)
        self.assertEqual(context['moc_id_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['title_term'], '')
        self.assertEqual(context['location_term'], '')
        self.assertEqual(context['site_config'], self.config)

        # Search box should inherit search terms.
        context = veteran_search_box_block.context(self.search_results_with_q_request)
        path = self.search_results_with_q_request.path
        q_term = self.search_results_with_q_request.GET['q']
        self.assertEqual(context['search_url'], path)
        self.assertEqual(context['moc_id_term'], '')
        self.assertEqual(context['moc_term'], '')
        self.assertEqual(context['title_term'], q_term)
        self.assertEqual(context['location_term'], '')
        self.assertEqual(context['site_config'], self.config)

    def test_page_all_blocks(self):
        blocks = []
        [blocks.append(factories.ContentBlockFactory()) for x in range(0, 5)]

        row = factories.RowFactory()
        [models.BlockOrder.objects.create(row=row, block=block,
                                          order=block.id)
         for block in blocks]

        [blocks.append(factories.LoginBlockFactory()) for x in range(0, 5)]

        row2 = factories.RowFactory()
        [models.BlockOrder.objects.create(row=row2, block=block,
                                          order=block.id)
         for block in blocks]

        page = factories.PageFactory(sites=(SeoSiteFactory(), ))
        models.RowOrder.objects.create(page=page, row=row,
                                       order=row.id)
        models.RowOrder.objects.create(page=page, row=row2,
                                       order=row2.id)

        all_blocks = page.all_blocks()
        all_blocks_ids = [block.id for block in all_blocks]
        block_ids = [block.id for block in blocks]

        self.assertItemsEqual(block_ids, all_blocks_ids)
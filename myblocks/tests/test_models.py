from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404

from myblocks import models
from myblocks.tests import factories
from myblocks.tests.setup import BlocksTestBase
from seo.tests.factories import SeoSiteFactory


class ModelsTests(BlocksTestBase):
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


        context = breadbox_block.context(self.search_results_with_q_request)
        breadbox = context['breadbox']
        self.assertEqual(breadbox.path, reverse('all_jobs'))

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

        # The context should contain the required context for both
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

    def test_row_context(self):
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory()
        breadbox_block = factories.BreadboxBlockFactory()

        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)

        context = row.context(self.search_results_request)
        keys = context.keys()

        # The context should contain the required context for both
        # blocks.
        expected_context = ['widgets', 'breadbox']
        for field in expected_context:
            self.assertIn(field, keys)
            self.assertIsNotNone(context[field])

    def test_row_template(self):
        one = 'template one'
        two = 'template two'

        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory(template=one)
        breadbox_block = factories.BreadboxBlockFactory(template=two)

        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)

        # Confirm that both templates are joined together in the correct order
        template = row.get_template()
        self.assertRegexpMatches(template, '.*%s.*%s.*' % (one, two))

        # Try a new order.
        reverse_row = factories.RowFactory()
        models.BlockOrder.objects.create(block=search_filter_block,
                                         row=reverse_row,
                                         order=2)
        models.BlockOrder.objects.create(block=breadbox_block,
                                         row=reverse_row,
                                         order=1)

        # Confirm that both templates are again joined in the correct order.
        template = reverse_row.get_template()
        self.assertRegexpMatches(template, '.*%s.*%s.*' % (two, one))

    def test_row_required_js(self):
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory()
        breadbox_block = factories.BreadboxBlockFactory()

        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)
        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=3)

        js = row.required_js()

        # Only SearchFilterBlock has expected js, and that js should be
        # included only once.
        search_filter_block_js = search_filter_block.required_js()
        self.assertEqual(len(js), len(search_filter_block_js))
        self.assertEqual(search_filter_block_js, js)

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

    def test_page_context(self):
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory()
        breadbox_block = factories.BreadboxBlockFactory()

        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)

        page = factories.PageFactory()
        models.RowOrder.objects.create(page=page, row=row, order=1)

        context = page.context(self.search_results_request)
        keys = context.keys()

        expected_context = ['widgets', 'breadbox', 'site_description',
                            'site_title']
        for field in expected_context:
            self.assertIn(field, keys)

    def test_page_get_head(self):
        one = 'head 1'
        two = 'head 2'
        three = 'head 3'

        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory(head=one)
        breadbox_block = factories.BreadboxBlockFactory(head=two)

        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)

        page = factories.PageFactory(head=three)
        models.RowOrder.objects.create(page=page, row=row, order=1)

        head = page.get_head()
        self.assertRegexpMatches(head, '.*%s.*%s.*%s.*' % (one, two, three))
        for js in search_filter_block.required_js():
            self.assertIn(js, head)

    def test_page_template(self):
        one = 'template one'
        two = 'template two'
        three = 'template three'
        four = 'template four'

        page = factories.PageFactory()

        # Row 1
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory(template=one)
        breadbox_block = factories.BreadboxBlockFactory(template=two)
        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)
        models.RowOrder.objects.create(page=page, row=row, order=1)

        # Row 2
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory(template=three)
        breadbox_block = factories.BreadboxBlockFactory(template=four)
        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)
        models.RowOrder.objects.create(page=page, row=row, order=2)

        # Confirm that both templates are joined together in the correct order
        template = page.get_template(self.search_results_request)
        pattern = '.*%s.*%s.*%s.*%s.*' % (one, two, three, four)
        self.assertRegexpMatches(template, pattern)

        # Try a new order.
        page = factories.PageFactory()

        # Row 1
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory(template=one)
        breadbox_block = factories.BreadboxBlockFactory(template=two)
        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=2)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=1)
        models.RowOrder.objects.create(page=page, row=row, order=1)

        # Row 2
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory(template=three)
        breadbox_block = factories.BreadboxBlockFactory(template=four)
        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=2)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=1)
        models.RowOrder.objects.create(page=page, row=row, order=2)

        # Confirm that both templates are joined together in the correct order
        template = page.get_template(self.search_results_request)
        pattern = '.*%s.*%s.*%s.*%s.*' % (two, one, four, three)
        self.assertRegexpMatches(template, pattern)

    def test_page_render_cache_prefix(self):
        """
        Changes to any part of a page should change the cache prefix.

        """
        row = factories.RowFactory()
        search_filter_block = factories.SearchFilterBlockFactory()
        breadbox_block = factories.BreadboxBlockFactory()

        models.BlockOrder.objects.create(block=search_filter_block, row=row,
                                         order=1)
        models.BlockOrder.objects.create(block=breadbox_block, row=row,
                                         order=2)

        page = factories.PageFactory()
        models.RowOrder.objects.create(page=page, row=row, order=1)

        start_prefix = page.render_cache_prefix(self.search_results_request)

        breadbox_block.save()

        end_prefix = page.render_cache_prefix(self.search_results_request)

        self.assertNotEqual(start_prefix, end_prefix)

    def test_page_handle_job_detail_redirect(self):
        page = factories.PageFactory(page_type=models.Page.JOB_DETAIL)

        # If there's a matching job and the url is correctly formatted
        # and the job belongs on that site there shouldn't be a redirect.
        redirect = page.handle_job_detail_redirect(self.job_detail_request,
                                                   **self.job_detail_kwargs)
        self.assertIsNone(redirect)

        # If there is no matching job it should result in a 404.
        self.assertRaises(Http404, page.handle_job_detail_redirect,
                          self.job_detail_request)

        # If the url is missing the slugs it should redirect to the
        # slugified version.
        redirect = page.handle_job_detail_redirect(self.job_detail_redirect_request,
                                                   job_id=self.job['guid'])
        self.assertEqual(self.job_detail_request.path, redirect.url)

        # If we don't have access to the job on this site it should
        # redirect to the home page.
        settings.SITE_BUIDS = settings.SITE_PACKAGES = [100]
        redirect = page.handle_job_detail_redirect(self.job_detail_request,
                                                   **self.job_detail_kwargs)
        self.assertEqual(redirect.url, reverse('home'))

    def test_page_handle_search_results_redirect(self):
        page = factories.PageFactory(page_type=models.Page.SEARCH_RESULTS)

        # If there are no jobs and no query string it should
        # redirect to the homepage.
        self.conn.delete(q='*:*')
        redirect = page.handle_search_results_redirect(self.search_results_request)
        self.assertEqual(redirect.url, reverse('home'))

        # But if there is a query string it should end up on the
        # no results found page.
        redirect = page.handle_search_results_redirect(self.search_results_with_q_request)
        self.assertIsNone(redirect)
# -*- coding: utf-8 -*-
from decimal import Decimal
from collections import namedtuple
from mock import patch

from django.conf import settings

from seo import helpers
from seo.models import CustomFacet
from seo.tests import factories
from setup import DirectSEOBase


class SeoHelpersTestCase(DirectSEOBase):
    """
    CustomFacets with count 0 should not be returned by get_solr_facet()
    unless CustomFacet.always_show = True.

    """
    def test_get_solr_facet_always_show(self):
        site_facet = factories.SeoSiteFacetFactory()
        site = site_facet.seosite
        settings.SITE_ID = site.pk
        settings.SITE = site
        custom_facet = site_facet.customfacet
        custom_facet.show_production = 1
        custom_facet.save()
        settings.STANDARD_FACET = [custom_facet]

        # The custom facet should have no results, and therefore should
        # not be in the list.
        result_counts = helpers.get_solr_facet([])
        self.assertEqual(len(result_counts), 0)

        custom_facet.always_show = True
        custom_facet.save()
        result_counts = helpers.get_solr_facet([])
        # If always_show is True the facet should be in the list even
        # if the count is 0.
        self.assertEqual(len(result_counts), 1)
        # The custom facet returned should be the one we created.
        self.assertEqual(result_counts[0][0], custom_facet)
        # The count should be 0.
        self.assertEqual(result_counts[0][1], 0)

    def test_featured_default_jobs(self):
        """
        Requests the number and offsets for featured and default jobs
        based on possible queryset job counts, offsets, and number of
        items requested.

        """
        p = Decimal(0.5)
        input_outputs = [
            #Getting jobs from sets of 25 featured andj
            #55 default, 50% split, in slices of 20 and 10
            ((25, 55, 20, p, 0), (10, 10, 0, 0)),
            ((25, 55, 20, p, 20), (10, 10, 10, 10)),
            ((25, 55, 20, p, 40), (5, 15, 20, 20)),
            ((25, 55, 10, p, 60), (0, 10, 30, 35)),
            ((25, 55, 20, p, 70), (0, 10, 35, 45)),
            #Offset higher than available jobs
            ((0, 50, 20, p, 50), (0, 0, 25, 50))
        ]
        io2 = []
        for i, o in input_outputs:
            #Reverse counts for featured and default jobs
            io2.append(((i[1], i[0], i[2], i[3], i[4]),
                        (o[1], o[0], o[3], o[2])))
            #No Featured Facet jobs
            io2.append(((0, 90, i[2], i[3], i[4]),
                        (0, i[2], int(i[4]*i[3]), i[4])))
        input_outputs.extend(io2)
        #Rounding should favor featured jobs. Here the first element to be
        #returned is a featured job, and the second is a default job
        input_outputs.append(((1, 1, 1, p, 0), (1, 0, 0, 0)))
        input_outputs.append(((1, 1, 1, p, 1), (0, 1, 1, 0)))

        for i, o in input_outputs:
            self.assertEqual(helpers.featured_default_jobs(*i), o)

    def test_breadcrumbs(self):
        job_dict = {'city': 'Indianapolis',
                    'city_slab': 'indianapolis/indiana/usa/jobs::Indianapolis, IN',
                    'country': 'United States',
                    'country_slab': 'usa/jobs::United States',
                    'state': 'Indiana',
                    'state_slab': 'indiana/usa/jobs::Indiana',
                    'title': 'Retail Associate',
                    'title_slab': 'retail-associate/jobs-in::Retail Associate'}

        field_list = " ".join(field for field in job_dict)
        jobTuple = namedtuple('jobTuple', field_list)
        job = jobTuple(*job_dict.values())

        breadcrumbs = helpers.job_breadcrumbs(job)
        city_path = breadcrumbs['city']['path']
        state_path = breadcrumbs['state']['path']
        title_path = breadcrumbs['title']['path']
        country_path = breadcrumbs['country']['path']
        self.assertEqual(city_path,
                         '/retail-associate/jobs-in/indiana/usa/jobs/')
        self.assertEqual(state_path,
                         '/retail-associate/jobs-in/usa/jobs/')
        self.assertEqual(title_path,
                         '/indianapolis/indiana/usa/jobs/')
        self.assertEqual(country_path,
                         '/retail-associate/jobs-in/')


class FuzzyInt(int):
    """
    Overrides the equal method in int to return true if an integer is within 
    the FuzzyInt's range. This let's us set a range for AssertNumQueries to
    make tests less brittle.

    """
    def __new__(cls, lowest, highest):
        obj = super(FuzzyInt, cls).__new__(cls, highest)
        obj.lowest = lowest
        obj.highest = highest
        return obj

    def __eq__(self, other):
        return self.lowest <= other <= self.highest

    def __repr__(self):
        return "[%d..%d]" % (self.lowest, self.highest)


class SeoHelpersDjangoTestCase(DirectSEOBase):

    @patch.object(CustomFacet, 'active_site_facet') 
    def test_sqs_apply_custom_facets(self, mock_active):
        """
        Tests that correct query strings are added to search query sets for
        different combinations of custom facets and exclude facets
        This is a regression test. Exclude facets weren't being applied when
        no custom facets were being passed in

        Since this is the first place we're using mock, here's a brief
        explanation. patch.object is a decorator that passes in 
        an object (in this case CustomFacet.active_site_facet) 
        to our function's local environment (where we've named it mock_active).
        We then override that objects behavior (it's return value in this case)
        to avoid having to set up a chain of sites and configurations
        just to get settings.SITE_ID set so that active_site_facet works
        correctly.

        """
        terms = [unicode(i) for i in range(10)]
        facets = CustomFacet.objects.all()
        self.assertEqual(len(facets), 0)
        facet_ids = [factories.CustomFacetFactory(title=term).id
                     for term in terms]
        facets = CustomFacet.objects.filter(id__in=facet_ids).order_by('title')
        [factories.SeoSiteFacetFactory(customfacet=facet) for facet in facets]

        site_facet = factories.SeoSiteFacetFactory()
        mock_active.return_value = site_facet

        for split in range(len(terms)):
            cf = facets.filter(title__in=terms[0:split]).order_by('title')
            ef = facets.filter(title__in=terms[split:]).order_by('title')

            with self.assertNumQueries(FuzzyInt(1, 10)):
                sqs = helpers.sqs_apply_custom_facets(custom_facets=cf,
                                                      exclude_facets=ef)

            # Narrow_queries is a set of querystrings. Our current
            # backend should build 1 string starting with NOT for exclude facets
            # and another string for custom facets
            queries = sqs.query.narrow_queries
            self.assertTrue(len(queries) > 0)
            for query in queries:
                if query.find(u'NOT') == -1:
                    present_terms = terms[0:split]
                    missing_terms = terms[split:]
                else:
                    present_terms = terms[split:]
                    missing_terms = terms[0:split]

                for term in present_terms:
                    self.assertNotEqual(query.find(term), -1)
                for term in missing_terms:
                    self.assertEqual(query.find(term), -1)
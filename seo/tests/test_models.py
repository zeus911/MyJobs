# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from seo.tests import factories
from seo.models import CustomFacet, SeoSite, SiteTag
from setup import DirectSEOBase


class ModelsTestCase(DirectSEOBase):
    """
    All tests that probe the *custom* functionality of models in the seo
    app belong here.

    """
    def test_unique_redirect(self):
        """
        Test to ensure that we can't create a redirect for the same
        SeoSite more than once (enforcing the "unique_together"
        constraint on the SeoSiteRedirect model.
        
        """
        site = factories.SeoSiteFactory()
        ssr1 = factories.SeoSiteRedirectFactory(seosite=site)
        ssr2 = factories.SeoSiteRedirectFactory.build()
        self.assertRaises(IntegrityError, ssr2.save, ())

    def test_config_inc(self):
        """
        Test that the Configuration instances associated with a
        particular SeoSite instance have their ``revision`` value
        incremented when the SeoSite is saved.
        
        """
        site = factories.SeoSiteFactory.build()
        site.save()
        config_staging = factories.ConfigurationFactory.build()
        config_staging.save()
        config_prod = factories.ConfigurationFactory.build(status=2)
        config_prod.save()
        site.configurations = [config_staging, config_prod]
        # The default value for the `revision` attribute is 1, and it's
        # incremented on save, so that means that even on the first save it gets
        # incremented to 2. So that's why we're testing against [2, 2] for two
        # new Configuration instances instead of [1, 1].
        self.assertItemsEqual([c.revision for c in site.configurations.all()],
                              [2, 2])
        # Make some arbitrary change to the SeoSite instance.
        site.site_heading = "We're changing the header! Call the cops!"
        site.save()
        self.assertItemsEqual([c.revision for c in site.configurations.all()],
                              [3, 3])

    def test_invalid_custom_facet(self):
        facet = CustomFacet()
        facet.city = facet.state = facet.country = facet.title = ' '
        facet.querystring = ")"
        self.assertRaises(ValidationError, facet.save)


class SeoSitePostAJobFiltersTestCase(DirectSEOBase):
    def setUp(self):
        super(SeoSitePostAJobFiltersTestCase, self).setUp()
        self.company = factories.CompanyFactory()
        self.company_buid = factories.BusinessUnitFactory()
        self.company.job_source_ids.add(self.company_buid)
        self.company.save()

    def create_generic_sites(self):
        sites = []
        for x in range(1, 15):
            factories.SeoSiteFactory()
        return sites

    def create_multiple_sites_for_company(self):
        sites = []
        for x in range(1, 15):
            site = factories.SeoSiteFactory()
            site.business_units.add(self.company_buid)
            site.save()
            sites.append(site)
        return sites

    def create_multiple_network_sites(self):
        network_tag, _ = SiteTag.objects.get_or_create(site_tag='network')

        sites = []
        for x in range(1, 15):
            site = factories.SeoSiteFactory()
            site.site_tags.add(network_tag)
            site.save()
            sites.append(site)
        return sites

    def test_network_sites(self):
        network_sites = self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'network sites only'}
        new_site = factories.SeoSiteFactory(**kwargs)

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        self.assertEqual(len(postajob_sites), len(network_sites))
        [self.assertIn(site.pk, postajob_site_ids) for site in network_sites]
        self.assertNotIn(new_site.pk, postajob_site_ids)

    def test_network_sites_and_this_site(self):
        network_sites = self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'network sites and this site'}
        new_site = factories.SeoSiteFactory(**kwargs)

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        self.assertEqual(len(postajob_sites), len(network_sites)+1)
        [self.assertIn(site.pk, postajob_site_ids) for site in network_sites]
        self.assertIn(new_site.pk, postajob_site_ids)

    def test_this_site_only(self):
        network_sites = self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        # 'this site only' is the default.
        new_site = factories.SeoSiteFactory()

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        self.assertEqual(len(postajob_sites), 1)
        [self.assertNotIn(site.pk, postajob_site_ids) for site in network_sites]
        self.assertIn(new_site.pk, postajob_site_ids)

    def test_company_sites(self):
        self.create_multiple_network_sites()
        company_sites = self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'sites associated with the company '
                                          'that owns this site'}
        new_site = factories.SeoSiteFactory(**kwargs)
        new_site.business_units.add(self.company_buid)
        new_site.save()

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        # postajob_sites = company_sites + new_site
        self.assertEqual(len(postajob_sites), len(company_sites)+1)
        [self.assertIn(site.pk, postajob_site_ids) for site in company_sites]

    def test_network_and_company_sites(self):
        network_sites = self.create_multiple_network_sites()
        company_sites = self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'network sites and sites associated '
                                          'with the company that owns this '
                                          'site'}
        new_site = factories.SeoSiteFactory(**kwargs)
        new_site.business_units.add(self.company_buid)
        new_site.save()

        postajob_sites = new_site.postajob_site_list()
        postajob_site_ids = [site.id for site in postajob_sites]

        # postajob_sites = company_sites + network_sites + new_site
        self.assertEqual(len(postajob_sites),
                         len(company_sites)+len(network_sites)+1)
        [self.assertIn(site.pk, postajob_site_ids) for site in company_sites]
        [self.assertIn(site.pk, postajob_site_ids) for site in network_sites]

    def test_all_sites(self):
        self.create_multiple_network_sites()
        self.create_multiple_sites_for_company()
        self.create_generic_sites()

        kwargs = {'postajob_filter_type': 'all sites'}
        new_site = factories.SeoSiteFactory(**kwargs)
        new_site.business_units.add(self.company_buid)
        new_site.save()

        postajob_sites = new_site.postajob_site_list()

        # postajob_sites = company_sites + network_sites + generic_sites +
        #                  new_site
        self.assertEqual(len(postajob_sites), SeoSite.objects.all().count())


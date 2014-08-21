# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from seo.tests import factories
from seo.models import CustomFacet
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
        site = factories.SeoSiteFactory.build()
        site.save()
        ssr1 = factories.SeoSiteRedirectFactory.build()
        ssr1.save()
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

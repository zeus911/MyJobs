import datetime

from django.conf import settings

from seo.tests.factories import (SeoSiteFactory, SeoSiteRedirectFactory)
from seo.models import BusinessUnit, SeoSite
from setup import DirectSEOBase


class SiteRedirectMiddlewareTestCase(DirectSEOBase):
    def setUp(self):
        super(SiteRedirectMiddlewareTestCase, self).setUp()
        self.test_site = SeoSiteFactory.build()
        self.test_site.save()
        self.ssr1 = SeoSiteRedirectFactory.build(seosite=self.test_site)
        self.ssr1.save()
        self.ssr2 = SeoSiteRedirectFactory.build(
                    redirect_url=u'test.%s' % self.test_site.domain,
                    seosite=self.test_site)
        self.ssr2.save()

    def test_host_is_a_redirect(self):
        """
        This tests that the passed in HOST needs to be redirected to
        another URL. The path that we go to is used to test that the
        path is consistent across redirects.
        
        """
        response = self.client.get(
            '/style/style.css',
            HTTP_HOST=u'.'.join([u'www', self.test_site.domain]),
            follow=True)
        redirect_url, status_code = response.redirect_chain[0]
        self.assertEqual(status_code, 301)
        self.assertEqual(redirect_url,
                         u'http://%s/style/style.css' % self.test_site.domain)

    def test_host_is_not_a_redirect(self):
        """
        This tests that the passed in HOST is the default domain name.
        
        """
        response = self.client.get('/style/style.css',
                                   HTTP_HOST=self.test_site.domain,
                                   follow=True)
        status_code = response.status_code
        redirect_chain = response.redirect_chain
        self.assertNotEqual(status_code, 301)
        # test here that there were no redirects, the chain should be empty
        self.assertEqual(len(redirect_chain), 0)

    def test_host_doesnt_exist(self):
        """
        Given our system, this one is a little tough to test, the URL
        is obviously not in the test database (not created in setup), so
        as long as it doesn't redirect, then I think this test passes.
        Yes...this is a little loose.

        """
        response = self.client.get('/', HTTP_HOST=u'buckconsultants.jobs', 
                                   follow=True)
        redirect_chain = response.redirect_chain
        self.assertEqual(len(redirect_chain), 0)


class MultiHostMiddlewareTestCase(DirectSEOBase):
    def setUp(self):
        super(MultiHostMiddlewareTestCase, self).setUp()
        self.bu = BusinessUnit(id=42, date_crawled=datetime.datetime.now(),
                               date_updated=datetime.datetime.now())
        self.test_site = SeoSiteFactory(
            domain=u'buckconsultants.jobs',
            name=u'buckconsultants')

    def test_existant_site(self):
        # test the site_id, site name, buids, etc
        self.client.get('/', HTTP_HOST=self.test_site.domain)
        self.assertEqual(settings.SITE_ID, self.test_site.id)
        self.assertEqual(settings.SITE_NAME, self.test_site.name)

    def test_non_existant_site(self):
        # The default site is secure.my.jobs, so compare all results to that.
        site = SeoSite.objects.get(domain='secure.my.jobs')

        # test that the site returned is the default site
        response = self.client.get('/', HTTP_HOST='jklsdasdfj.jobs')
        self.assertEqual(settings.SITE_ID, site.id)
        self.assertEqual(settings.SITE_NAME, site.name)
        self.assertEqual(len(settings.SITE_BUIDS), site.business_units.all().count())

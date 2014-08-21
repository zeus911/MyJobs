from django.conf import settings

from seo.tests.setup import DirectSEOBase
from seo.tests.factories import SeoSiteFactory


class WildcardMiddlewareTestCase(DirectSEOBase):
    def test_wildcard_redirect(self):
        """
        Test the wildcard redirect. This makes a call to a url with an invalid
        subdomain, which should result in a 301 redirect to the root domain.
        
        """
        site = SeoSiteFactory.build(domain='www.my.jobs',name=u'www.my.jobs')
        site.save()
        
        settings.WILDCARD_REDIRECT = True
        # check that the redirect ignores domains without a subdomain
        resp = self.client.get('/', HTTP_HOST='domain.jobs')
        self.assertEqual(resp.status_code, 200)
        
        # check that IP addresses are NOT redirected 
        resp = self.client.get('/', HTTP_HOST='127.0.0.1') 
        self.assertEqual(resp.status_code, 200)
        
        # check that the redirect ignores domains in the exception list
        resp = self.client.get(
            '/', 
            HTTP_HOST='ec2-50-16-227-119.compute-1.amazonaws.com'
            )
        self.assertEqual(resp.status_code, 200)
        
        # check that it redirects when it supposed to
        resp = self.client.get('/', HTTP_HOST='fake.usa.jobs', follow=True)
        self.assertEqual(resp.status_code, 301)        
        WildcardMiddlewareTestCase._check_external_redirect(self,
            resp,"http://usa.jobs")
        
        # check that is respects the setting toggle
        settings.WILDCARD_REDIRECT = False
        resp = self.client.get('/', HTTP_HOST='wrong.www.my.jobs')
        self.assertEqual(resp.status_code, 200)        
        
    def _check_external_redirect(obj,resp,target):
        """
        Checks a given external redirect for success. testClient can't access 
        external links, so we can't test for its response code. It's still 
        necesarry to check the redirect target.
        
        Inputs:
        :obj:       the testClient object from the calling method
        :resp:      the testClient response object from the calling method
        :target:    the url string where the redirect should have ended
        
        """
        obj.assertRedirects(resp,target,status_code=301,target_status_code=301)
        

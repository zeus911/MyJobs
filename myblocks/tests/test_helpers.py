from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from myblocks import helpers
from seo.tests.setup import DirectSEOBase


class HelpersTests(DirectSEOBase):
    def test_success_url(self):
        request = RequestFactory()
        setattr(request, 'REQUEST', {})
        self.assertEqual(helpers.success_url(request), reverse('home'))

        url = 'https://www.my.jobs/'
        setattr(request, 'REQUEST', {'next': url})
        self.assertEqual(helpers.success_url(request), url)
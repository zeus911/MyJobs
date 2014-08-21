from seo.templatetags.seo_extras import build_rss_link
from setup import DirectSEOBase


class SeoExtrasTestCase(DirectSEOBase):
    def test_build_rss_link(self):
        rss = build_rss_link('http://indianapolis.jobs/search?q=query')
        self.assertEqual(rss, 'http://indianapolis.jobs/search/feed/rss?q=query')
        rss = build_rss_link('http://indianapolis.jobs/jobs/')
        self.assertEqual(rss, 'http://indianapolis.jobs/jobs/feed/rss')

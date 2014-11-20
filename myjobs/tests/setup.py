from seo_pysolr import Solr

from django.core.cache import cache
from django.core.urlresolvers import clear_url_caches
from django.test import TestCase


class MyJobsBase(TestCase):
    def setUp(self):
        from django.conf import settings
        setattr(settings, 'ROOT_URLCONF', 'myjobs_urls')
        cache.clear()
        clear_url_caches()
        self.ms_solr = Solr('http://127.0.0.1:8983/solr/seo')
        self.ms_solr.delete(q='*:*')

    def tearDown(self):
        self.ms_solr.delete(q='*:*')
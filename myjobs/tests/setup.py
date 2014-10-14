from pysolr import Solr

from django.core.cache import cache
from django.test import TestCase


class MyJobsBase(TestCase):
    def setUp(self):
        from django.conf import settings
        setattr(settings, 'ROOT_URLCONF', 'myjobs_urls')
        cache.clear()
        self.ms_solr = Solr('http://127.0.0.1:8983/solr/seo')
        self.ms_solr.delete(q='*:*')
        self.assertEqual(self.ms_solr.search('*:*').hits, 0)

    def tearDown(self):
        self.ms_solr.delete(q='*:*')
        self.assertEqual(self.ms_solr.search('*:*').hits, 0)
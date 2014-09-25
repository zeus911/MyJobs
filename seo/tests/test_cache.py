# -*- coding: utf-8 -*-
from django.conf import settings

from seo.cache import get_facet_count_key
from seo.helpers import build_filter_dict
from setup import DirectSEOBase


class SeoCacheTestCase(DirectSEOBase):
    def test_get_facet_count_key(self):
        """
        Tests that we're getting unique or matching cache keys based on
        filter paths
        
        """
        filters1 = build_filter_dict('/standard-facet/new-jobs/dubuque/jobs/')
        filters2 = build_filter_dict('/特殊字符/new-jobs/')
        filters3 = build_filter_dict('/dubuque/jobs/standard-facet/new-jobs/')

        key1 = get_facet_count_key(filters1)
        key2 = get_facet_count_key(filters2)
        key3 = get_facet_count_key(filters3)
        settings.SITE_ID = 10
        key4 = get_facet_count_key(filters1)

        self.assertNotEqual(key2, key3)
        self.assertNotEqual(key2, key1)
        self.assertNotEqual(key4, key1)
        self.assertEqual(key1, key3)



from django.core.cache import cache
from django.test import TestCase


class MyJobsBase(TestCase):
    def setUp(self):
        from django.conf import settings
        setattr(settings, 'ROOT_URLCONF', 'myjobs_urls')
        cache.clear()

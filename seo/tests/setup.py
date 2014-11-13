import os.path
from contextlib import contextmanager

from django.core.cache import cache
from django.core.urlresolvers import clear_url_caches
from django.db import connections
from django.test import TestCase

from seo_pysolr import Solr
from import_jobs import DATA_DIR
from seo.tests.factories import BusinessUnitFactory
import solr_settings


class DirectSEOBase(TestCase):
    def setUp(self):
        from django.conf import settings
        from django.template import context

        db_backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]

        # Set columns that are utf8 in production to utf8
        if db_backend == 'mysql':
            cursor = connections['default'].cursor()
            cursor.execute("alter table seo_customfacet convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_seositefacet convert to character "
                           "set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_company convert to character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table taggit_tag convert to character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table taggit_taggeditem convert to "
                           "character set "
                           "utf8 collate utf8_unicode_ci")
            cursor.execute("alter table seo_seositeredirect convert to "
                           "character set utf8 collate utf8_unicode_ci")
            cursor.execute("alter table django_redirect convert to "
                           "character set utf8 collate utf8_unicode_ci")

        setattr(settings, 'ROOT_URLCONF', 'dseo_urls')
        clear_url_caches()

        self.base_middleware_classes = settings.MIDDLEWARE_CLASSES
        middleware_classes = self.base_middleware_classes + (
            'wildcard.middleware.WildcardMiddleware', )
        setattr(settings, 'MIDDLEWARE_CLASSES', middleware_classes)

        self.base_context_processors = settings.TEMPLATE_CONTEXT_PROCESSORS
        context_processors = self.base_context_processors + (
            "social_links.context_processors.social_links_context",
            "seo.context_processors.site_config_context",
        )
        setattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS', context_processors)
        context._standard_context_processors = None

        self.conn = Solr('http://127.0.0.1:8983/solr/seo')
        self.conn.delete(q="*:*")
        cache.clear()
        clear_url_caches()

    def tearDown(self):
        from django.conf import settings
        from django.template import context

        setattr(settings, 'TEMPLATE_CONTEXT_PROCESSORS',
                self.base_context_processors)
        context._standard_context_processors = None
        setattr(settings, 'MIDDLEWARE_CLASSES',
                self.base_middleware_classes)


class DirectSEOTestCase(DirectSEOBase):
    def setUp(self):
        super(DirectSEOTestCase, self).setUp()
        self.solr_docs = solr_settings.SOLR_FIXTURE
        self.conn.add(self.solr_docs)

        #uids and numjobs in feed file for test business unit 0
        self.feed_uids = [25599525, 25599523, 25611673, 25622522]
        self.feed_numjobs = 4

        self.businessunit = BusinessUnitFactory(id=0)
        self.buid_id = self.businessunit.id        
        #Ensure DATA_DIR used by import_jobs.download_feed_file exists
        data_path = DATA_DIR
        if not os.path.exists(data_path):
            os.mkdir(data_path)

    def tearDown(self):
        super(DirectSEOTestCase, self).tearDown()
        self.conn.delete(q="*:*")
        self.assertEqual(self.conn.search(q='*:*').hits, 0)


class SettingDoesNotExist:
    pass


@contextmanager
def patch_settings(**kwargs):
    from django.conf import settings
    old_settings = []
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings.append((key, old_value))
        setattr(settings, key, new_value)
    yield

    for key, old_value in old_settings:
        if old_value is SettingDoesNotExist:
            delattr(settings, key)
        else:
            setattr(settings, key, old_value)

@contextmanager
def connection(**kwargs):
    from haystack import connections

    for key, new_value in kwargs.items():
        setattr(connections, key, new_value)
        connections['default'].options['URL'] = connections.connections_info['default']['URL']
    yield

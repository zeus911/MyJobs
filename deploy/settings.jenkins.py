from default_settings import *

DEBUG = True

ABSOLUTE_URL = "/"

PROJECT = 'myjobs'
ENVIRONMENT = 'Jenkins'

DATABASES = {
    'default': {
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'de_dbuser',
        'PASSWORD': PROD_DB_PASSWD,
        'HOST': 'db-redirectstaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
}
SOLR = {
    'all': 'http://127.0.0.1:8983/solr/myjobs_test/',
    'current': 'http://127.0.0.1:8983/solr/myjobs_test_current/',
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'


JENKINS_TEST_RUNNER = 'silent_testrunner.SilentTestRunner'
TEST_SOLR_INSTANCE = SOLR
CELERY_ALWAYS_EAGER = True

CC_AUTH = TESTING_CC_AUTH

ALLOWED_HOSTS = ['*', ]

ROOT_URLCONF = 'myjobs_urls'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/seo',
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password'],
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://127.0.0.1:8983/solr/seo',
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password'],
    },
}

TEMPLATE_CONTEXT_PROCESSORS += (
    'mymessages.context_processors.message_lists',
)

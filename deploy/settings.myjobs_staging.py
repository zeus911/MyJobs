from S3 import CallingFormat
from default_settings import *
import datetime
import os

DEBUG = True

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

ALLOWED_HOSTS = ['my.jobs', 'localhost']

_PATH = os.path.abspath(os.path.dirname(__file__))


# Absolute URL used for cross site links, relative during local/staging
# absolute during production
ABSOLUTE_URL = '/'

SESSION_CACHE_ALIAS = 'sessions'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime('.'))),
        'LOCATION': [
            'staging-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211'
        ]
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'staging-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211'
        ]
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SOLR = {
    'all': 'http://127.0.0.1:8983/solr/myjobs/',
    'current': 'http://127.0.0.1:8983/solr/myjobs_current/',
}

AWS_STORAGE_BUCKET_NAME = 'my-jobs'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

POSTAJOB_URLS = {
    'post': 'http://50.19.231.150/ajax/postajob/',
    'delete': 'http://50.19.231.150/ajax/deleteajob/'
}

CC_AUTH = TESTING_CC_AUTH

ROOT_URLCONF = 'myjobs_urls'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/microsites',
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://127.0.0.1:8983/solr/microsites',
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
  }
}
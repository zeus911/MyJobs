import datetime
from S3 import CallingFormat

from default_settings import *
from dseo_celery import *
from secrets import PROD_DB_PASSWD, SOLR_AUTH


ALLOWED_HOSTS = ['*', ]

DATABASES = {'default': {'NAME': 'redirect',
                         'ENGINE': 'django.db.backends.mysql',
                         'USER': 'db_deuser',
                         'PASSWORD': PROD_DB_PASSWD,
                         'HOST': 'db-redirect.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
                         'PORT': '3306', }
            }

TEMPLATE_DIRS = (
    '/home/web/MyJobs/MyJobs/templates/',
)

SESSION_CACHE_ALIAS = 'sessions'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # Set version number to date that this file was last modified
        # This should update the cache key on deployments and ensure any servers
        # deployed to on the same day will have matching keys. This won't clear 
        # the cache for multiple deployments per day.
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime(__file__))),
        'LOCATION': [
            'dseo-mc-cluster.qksjst.0003.use1.cache.amazonaws.com:11211',
            'dseo-mc-cluster.qksjst.0004.use1.cache.amazonaws.com:11211',
        ]
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'dseomj-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0002.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0003.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0004.use1.cache.amazonaws.com:11211',
        ]
    },
}

# Add newrelic here since it shouldn't be used on non-production servers
NEW_RELIC_TRACKING = True
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('middleware.NewRelic',)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        # 'solr_server' must be defined in /etc/hosts on the server where this
        # code is deployed. Check the deployment project in
        # direct_seo/web/conf/hosts and make sure the one in production looks
        # like that.
        'URL': 'http://solr_server/solr',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://solr_server/solr',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    }
}

AWS_STORAGE_BUCKET_NAME = 'src-nlx-org'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

ROOT_URLCONF = 'dseo_urls'
MIDDLEWARE_CLASSES += ('wildcard.middleware.WildcardMiddleware', )
TEMPLATE_CONTEXT_PROCESSORS += (
    "social_links.context_processors.social_links_context",
    "seo.context_processors.site_config_context",
)

SOLR = {
    'all': 'http://ec2-23-20-67-65.compute-1.amazonaws.com:8983/solr/myjobs_test/',
    'current': 'http://ec2-23-20-67-65.compute-1.amazonaws.com:8983/solr/myjobs_test_current/',
    }

ABSOLUTE_URL = '/'

STATIC_URL = "//d2e48ltfsb5exy.cloudfront.net/content_ms/files/"
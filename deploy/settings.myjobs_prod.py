from S3 import CallingFormat
from default_settings import *
import datetime
import os

DEBUG = False


DATABASES = {'default': {'NAME': 'redirect',
                         'ENGINE': 'django.db.backends.mysql',
                         'USER': 'db_deuser',
                         'PASSWORD': PROD_DB_PASSWD,
                         'HOST': 'db-redirect.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
                         'PORT': '3306', }
            }

ALLOWED_HOSTS = ['secure.my.jobs', 'my.jobs', 'localhost']

# Add newrelic here since it shouldn't be used on non-production servers
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('middleware.NewRelic',)
NEW_RELIC_TRACKING = True

# Ensure that https requests to Nginx are treated as secure when forwarded
# to MyJobs
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Browsers should only send the user's session cookie over https
SESSION_COOKIE_SECURE = True

STATIC_URL = "//d2e48ltfsb5exy.cloudfront.net/content_mj/files/"

# Absolute URL used for cross site links, relative during local/staging
# absolute during production
ABSOLUTE_URL = "https://secure.my.jobs/"

PROJECT = "myjobs"

SESSION_CACHE_ALIAS = 'sessions'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime('.'))),
        'LOCATION': [
            'dseomj-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211',
            'dseomj-mc-cluster.qksjst.0002.use1.cache.amazonaws.com:11211',
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
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SOLR = {
    'all': 'http://ec2-54-87-235-123.compute-1.amazonaws.com:8080/solr/profiles/',
    'current': 'http://ec2-54-87-235-123.compute-1.amazonaws.com:8080/solr/profiles_current/',
}

AWS_STORAGE_BUCKET_NAME = 'my-jobs'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

CC_AUTH = PROD_CC_AUTH

ROOT_URLCONF = 'myjobs_urls'


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'seo.search_backend.DESolrEngine',
        # 'solr_server' must be defined in /etc/hosts on the server where this
        # code is deployed. Check the deployment project in
        # direct_seo/web/conf/hosts and make sure the one in production looks
        # like that.
        'URL': 'http://solr_server:8983/solr',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    },
    'groups': {
        'ENGINE': 'saved_search.groupsearch.SolrGrpEngine',
        'URL': 'http://solr_server:8983/solr',
        'TIMEOUT': 300,
        'HTTP_AUTH_USERNAME': SOLR_AUTH['username'],
        'HTTP_AUTH_PASSWORD': SOLR_AUTH['password']
    }
}

BROKER_HOST = '204.236.236.123'
BROKER_PORT = 5672
BROKER_USER = 'celery'
BROKER_VHOST = 'dseo-vhost'

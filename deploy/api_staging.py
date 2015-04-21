from secrets import *
from default_settings import *


ALLOWED_HOSTS = ['*', ]

DATABASES = {
    'default': {
        'NAME': 'redirect',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'de_dbuser',
        'PASSWORD': PROD_DB_PASSWD,
        'HOST': 'db-redirectstaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
    'api': {
        'NAME': 'api',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'de_dbuser',
        'PASSWORD': PROD_DB_PASSWD,
        'HOST': 'db-redirectstaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
}

DEBUG = True

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
}

ROOT_URLCONF = 'api_urls'

PROJECT = 'api'

SOLR = {
    'all': 'http://ec2-23-20-67-65.compute-1.amazonaws.com:8983/solr/myjobs_test/',
    'current': 'http://ec2-23-20-67-65.compute-1.amazonaws.com:8983/solr/myjobs_test_current/',
}
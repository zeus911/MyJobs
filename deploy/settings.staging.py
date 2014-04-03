from S3 import CallingFormat
from secrets import PROD_DB_PASSWD
from default_settings import *
import datetime
import os

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'dseo_mj',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'dseo_mj',
        'PASSWORD': PROD_DB_PASSWD,
        'HOST': 'db-dseomjstaging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    },
}

ALLOWED_HOSTS = ['my.jobs', 'localhost']

_PATH = os.path.abspath(os.path.dirname(__file__))

STATIC_ROOT = os.path.join(_PATH, 'files', 'static')
STATIC_URL = '/files/'

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
    'default': 'http://127.0.0.1:8983/solr/myjobs/',
}

AWS_STORAGE_BUCKET_NAME = 'my-jobs'
AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
from secrets import PROD_DB_PASSWD
from default_settings import *

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'VERSION': str(datetime.date.fromtimestamp(os.path.getmtime('.'))),
        'LOCATION': [
            'staging-mc-cluster.qksjst.0001.use1.cache.amazonaws.com:11211'
        ]
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

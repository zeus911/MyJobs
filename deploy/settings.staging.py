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


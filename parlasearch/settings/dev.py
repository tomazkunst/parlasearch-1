# -*- coding: utf-8 -*-
from .default import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hashhashhashhashashwkopaskfpjoivanijfdsf2332fdw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEVELOPMENT = False

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'parlalize',
        'USER': 'parlauser',
        'PASSWORD': 'parlapassword',
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


API_URL = "http://localhost:8000/v1"

ANALIZE_URL = 'http://localhost:8080/v1'

SOLR_URL = 'http://localhost:8983/solr/parlameter'

BASE_URL = 'https://localhost'

DASHBOARD_URL = 'http://localhost:8881'

RAVEN_CONFIG = {
    #'dsn': 'http://123sdfsd123:123gdfsg123@sentry.url.si/40',
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

PARLALIZE_API_KEY = "nekijabolteskega"


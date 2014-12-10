from __future__ import absolute_import, unicode_literals
import os
import sys


DEBUG = False
TEMPLATE_DEBUG = DEBUG
TIME_ZONE = "GB"
USE_TZ = True
LANGUAGE_CODE = "en_GB"
USE_I18N = True
USE_L10N = True
INSTALLED_APPS = (
    "instance",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
)
ROOT_URLCONF = 'instance.urls'
ALLOWED_HOSTS = ['*']
STATICFILES_FINDERS = (
    "instance.finder.CurrentSiteStaticFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

TEMPLATE_LOADERS = (
    'instance.loader.CurrentSiteLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
)
MIDDLEWARE_CLASSES = []

###########
# LOGGING #
###########
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'standard': {
            'format': '[%(threadName)s] %(levelname)s %(asctime)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'instance': {
            'handlers': ['console'],
            'level': 'INFO'
        },
    }
}

WSGI_APPLICATION = 'instance.wsgi.application'
SECRET_KEY = 'notasecret'
DATABASES = {
}



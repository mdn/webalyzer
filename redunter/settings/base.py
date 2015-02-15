"""
Django settings for redunter project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

import dj_database_url
from decouple import Csv, config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)
DEBUG_PROPAGATE_EXCEPTIONS = config(
    'DEBUG_PROPAGATE_EXCEPTIONS', default=False, cast=bool)

TEMPLATE_DEBUG = config('DEBUG', default=DEBUG, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    # Project specific apps
    'redunter.base',
    'redunter.collector',
    'redunter.analyzer',

    # Third party apps
    'django_nose',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

for app in config('EXTRA_APPS', default='', cast=Csv()):
    INSTALLED_APPS.append(app)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'csp.middleware.CSPMiddleware',
)

ROOT_URLCONF = 'redunter.urls'

WSGI_APPLICATION = 'redunter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': config(
        'DATABASE_URL',
        cast=dj_database_url.parse
    )
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = config('USE_I18N', default=True, cast=bool)

USE_L10N = config('USE_L10N', default=True, cast=bool)

USE_TZ = config('USE_TZ', default=True, cast=bool)

STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'static'))
STATIC_URL = config('STATIC_URL', '/static/')

MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
MEDIA_URL = config('MEDIA_URL', '/media/')

SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)

TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Django-CSP
#CSP_DEFAULT_SRC = (
#    "'self'",
#)
#CSP_FONT_SRC = (
#    "'self'",
#    'http://*.mozilla.net',
#    'https://*.mozilla.net',
#    'http://fonts.gstatic.com',
#    'https://fonts.gstatic.com',
#)
#CSP_IMG_SRC = (
#    "'self'",
#    'http://*.mozilla.net',
#    'https://*.mozilla.net',
#)
#CSP_SCRIPT_SRC = (
#    "'self'",
#)
#CSP_STYLE_SRC = (
#    "'self'",
#    "'unsafe-inline'",
#    'http://www.mozilla.org',
#    'https://www.mozilla.org',
#    'http://*.mozilla.net',
#    'https://*.mozilla.net',
#    'http://fonts.googleapis.com',
#    'https://fonts.googleapis.com',
#)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


ALLIGATOR_CONN = config('ALLIGATOR_CONN', default='redis://localhost:6379/1')

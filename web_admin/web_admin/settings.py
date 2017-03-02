"""
Django settings for web_admin project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dvph%ti#3)^p^a)+pmi*mv)j%)_4rq)302()yx-_lpj4-!(9_x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mod_wsgi.server',

    'authentications',
    'client_credentials',
    'web',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOG_DIR = '/data/logs/admin-portal'
LOG_FILENAME = os.path.join(LOG_DIR, 'ami-admin-portal.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] | %(levelname)s | %(threadName)s | ami-admin-portal | %(name)s.%(funcName)s:%(lineno)s | %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': LOG_FILENAME,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'authentications': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'authentications': {
            'handlers': ['file'],
            'level': 'ERROR',
        },
        'client_credentials': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'client_credentials': {
            'handlers': ['file'],
            'level': 'ERROR',
        },
    }
}

# Load configuration from configuration file
sys.path.append('/data/projects/admin-portal/config')

from platform_settings import *

AUTHENTICATION_BACKENDS = ('authentications.apps.CustomBackend', )
# Add this to tell Django where to redirect after
# successful login

ROOT_URLCONF = 'web_admin.urls'

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(PROJECT_PATH, 'web', 'templates', 'client_credentials', 'oauth_client')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/admin-portal/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

WSGI_APPLICATION = 'web_admin.wsgi.application'



# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases



# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = 'home'
# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True





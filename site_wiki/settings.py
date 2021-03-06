"""
Django settings for site_wiki project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import socket
import importlib

filename = "settings_local_"+socket.gethostname()
filename = filename.replace("-","_")

settings_local = importlib.import_module("." + filename, "site_wiki")
#import settings_local_crymal_VirtualBox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hk8@0lef88isdjexgm7(e4xg^7%f4wbjpx*cf2h!xh+ru2t=sn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# only server site through these addresses
#ALLOWED_HOSTS = ['192.168.56.2','*']
#ALLOWED_HOSTS = ['192.168.56.2']
ALLOWED_HOSTS = ['192.168.56.2','10.0.2.15']

# allows debug info only when request comes from theses addresses
INTERNAL_IPS = ['192.168.56.1']

#ADMINS = (('crymal',''),)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myauth',
    'task',
    'sheets',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'site_wiki.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'site_wiki.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE="US/Pacific"

USE_I18N = True

USE_L10N = True

USE_TZ = True


AUTH_USER_MODEL = 'myauth.MyUser'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static_site_work/'

STATIC_ROOT = '/home/crymal/static/site_work'

WIKI_SOURCE_DIR     = settings_local.WIKI_SOURCE_DIR
WIKI_BUILD_DIR      = settings_local.WIKI_BUILD_DIR
WIKI_SEMISTATIC_DIR = settings_local.WIKI_SEMISTATIC_DIR
WIKI_STATIC_DIR = settings_local.WIKI_STATIC_DIR


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    WIKI_SEMISTATIC_DIR,
    WIKI_STATIC_DIR,
)

# email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.office365.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
#EMAIL_USE_SSL = False
#EMAIL_HOST_USER = "charles.rymal@nortek.com"
EMAIL_HOST_USER = "CR3B88@nortek.com"
EMAIL_HOST_PASSWORD = "Alpineglacierlemon1"

prefix = '/site_work/'

LOGIN_REDIRECT_URL = prefix + 'accounts/login/'
LOGIN_URL = prefix + 'accounts/login/'
LOGOUT_URL = prefix + 'accounts/logout/'



"""
Django settings for apicvf_django project.

Generated by 'django-admin startproject' using Django 2.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7x51b)i%*qy)tb^ckb^nmk^39x^gq-wp$2nq+%40yj0)4srb!='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Get the db according to the architecture the plugin's on
LOCAL_VM = True


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'carto',
    'procedere',
    'epistola',
    'parameters',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'apicvf_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'apicvf_django.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
if DEBUG and LOCAL_VM :
    DATABASES = {
        'default': {       
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'plugin_apicvf_base',
            'USER': 'metwork',
            'PASSWORD': 'metwork',
            'HOST': 'localhost',
            'PORT': '7432',
        }
     
    }
else :
    DATABASES = {
        'default': {       
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'plugin_apicvf_base',
            'USER': 'metwork',
            'PASSWORD': 'metwork',
            'HOST': 'apicb31-sidev',
            'PORT': '7432',
        }
    }
    

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# ADDED BY METWORK/MFSERV/DJANGO PLUGIN TEMPLATE
# TO PROVIDE PREFIX BASED ROUTING
STATIC_URL = '/apicvf_django/apicvf_django/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "apicvf_django/static")

# ADDED BY METWORK/MFSERV/DJANGO PLUGIN TEMPLATE
# TO PROVIDE DEBUG FEATURE
DEBUG = (os.environ.get('MFSERV_CURRENT_PLUGIN_DEBUG', '0') == '1')
import mflog
if DEBUG:
    mflog.set_config(minimal_level="DEBUG")
else:
    mflog.set_config()

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

if not LOCAL_VM:
    ALLOWED_HOSTS.append('apicf31-sidev')

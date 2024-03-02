"""
Django settings for biodiversity project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
import dj_database_url
from celery.schedules import crontab


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'hello')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = json.loads(os.getenv('DEBUG', 'false'))
DEBUG_PROPAGATE_EXCEPTIONS = json.loads(
    os.getenv('DEBUG_PROPAGATE_EXCEPTIONS', 'true'))

USE_HTTPS = json.loads(os.getenv('USE_HTTPS', 'false'))

SITE_ID = int(os.getenv('SITE_ID', '1'))

ALLOWED_HOSTS = json.loads(os.getenv('ALLOWED_HOSTS', '["*"]'))
CSRF_TRUSTED_ORIGINS = json.loads(os.getenv(
    'CSRF_TRUSTED_ORIGINS', '["https://denr-penro-8a40c4e87d0b.herokuapp.com"]'))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'phonenumber_field',
    'django_yubin',
    'dal',
    'dal_select2',
    'ajax_select',
    'django_filters',
    'storages',
    'django_vite',

    'users',
    'animals',
    'permits',
    'payments'
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biodiversity.urls'

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
                'biodiversity.context_processors.custom_global_vars',
            ],
        },
    },
]

WSGI_APPLICATION = 'biodiversity.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if DEBUG:
    DATABASES['default']['ENGINE'] = os.environ.get(
        'DB_ENGINE', 'django.db.backends.postgresql')
    DATABASES['default']['NAME'] = os.environ.get('DB_NAME', 'biodiversity_db')
    DATABASES['default']['USER'] = os.environ.get('DB_USER', 'denr')
    DATABASES['default']['PASSWORD'] = os.environ.get('DB_PASSWORD', 'denr')
    DATABASES['default']['HOST'] = os.environ.get('DB_HOST', 'db')
    DATABASES['default']['PORT'] = os.environ.get('DB_PORT', '5432')
else:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    db_from_env = dj_database_url.config(
        default=DATABASE_URL, conn_max_age=500, ssl_require=True)
    DATABASES['default'].update(db_from_env)

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ANONYMOUS_USER_NAME = None

LOGIN_URL = 'login'

LOGOUT_REDIRECT_URL = 'login'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

USE_S3 = json.loads(os.getenv('USE_S3', 'false'))
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/dist/'
]
if USE_S3:
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'no-cache'}
    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'biodiversity.storage_backends.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'biodiversity.storage_backends.PrivateMediaStorage'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_FILE_STORAGE = 'biodiversity.storage_backends.PrivateMediaStorage'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MAX_UPLOADED_FILE_SIZE_MB = int(os.getenv('MAX_UPLOADED_FILE_SIZE_MB', '5'))


# EMAILS

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND', 'sendgrid_backend.SendgridBackend')

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

SENDGRID_SANDBOX_MODE_IN_DEBUG = json.loads(
    os.getenv('SENDGRID_SANDBOX_MODE_IN_DEBUG', 'false'))

DEFAULT_FROM_EMAIL = os.getenv(
    'DEFAULT_FROM_EMAIL', 'PENRO <denniel@lambda-tech.ph>')

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.sendgrid.net')

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'apikey')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

EMAIL_PORT = os.getenv('EMAIL_PORT', '587')

EMAIL_USE_TLS = json.loads(os.getenv('EMAIL_USE_TLS', 'false'))


# PHONE

PHONENUMBER_DB_FORMAT = 'NATIONAL'

PHONENUMBER_DEFAULT_REGION = 'PH'


# TIME

TIME_ZONE = 'Asia/Manila'


# LOGGING

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '[%(asctime)s: %(levelname)s/%(name)s:%(lineno)d] %(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': LOG_LEVEL,
        },
    },
}


# CELERY

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379')

CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CELERY_WORKER_CONCURRENCY = int(os.getenv('CELERY_WORKER_CONCURRENCY', '4'))

CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    'check_permit_validity': {
        'task': 'permits.tasks.check_permit_validity',
        'schedule': crontab(minute=0, hour=0)
    }
}


# Permits

VALIDITY = {
    'LocalTransportPermit': int(os.getenv('VALIDITY_DAYS_LTP', '30')),
    'WildlifeFarmPermit': int(os.getenv('VALIDITY_DAYS_WFP', '1825')),
    'WildlifeCollectorPermit': int(os.getenv('VALIDITY_DAYS_WCP', '1825')),
    'CertificateOfWildlifeRegistration': int(os.getenv('VALIDITY_DAYS_CWR', '30')),
    'GratuitousPermit': int(os.getenv('VALIDITY_DAYS_GP', '30'))
}


# PAYMONGO

PAYMONGO = {
    'SECRET_KEY': os.getenv('PAYMONGO_SECRET_KEY'),
    'STATEMENT_DESCRIPTOR': os.getenv('PAYMONGO_STATEMENT_DESCRIPTOR', 'DENR-PENRO')
}


DJANGO_VITE = {
    'default': {
        'dev_mode': True,
        'manifest_path': BASE_DIR / 'frontend/dist/.vite/manifest.json'
    }
}

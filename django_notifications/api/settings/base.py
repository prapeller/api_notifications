import os
from pathlib import Path

from api.settings.timezones import TIMEZONES_DICT
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CORE_APPS_DIR = ROOT_DIR / "core_apps"

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
]

THIRD_PARTY_APPS = []

CORE_APPS = [
    "core_apps.notifications",
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

DEBUG = os.environ.get('DEBUG', False) == 'True'
DOCKER = os.environ.get('DOCKER', True) == 'True'

if DEBUG and not DOCKER:
    load_dotenv(ROOT_DIR / '../.envs/.local/.django')
    load_dotenv(ROOT_DIR / '../.envs/.local/.postgres')
    THIRD_PARTY_APPS.append('corsheaders')
    MIDDLEWARE.insert(2, "corsheaders.middleware.CorsMiddleware")
    CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CORE_APPS

ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = TIMEZONES_DICT.get('UTC+3')
LOCAL_PATHS = ['core_apps/notifications/locale']

USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = "/staticfiles/"
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
STATICFILES_DIRS = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = str(ROOT_DIR / "mediafiles")

SERVICE_TO_SERVICE_SECRET = os.getenv('SERVICE_TO_SERVICE_SECRET')
API_NOTIFICATIONS_HOST = os.getenv('API_NOTIFICATIONS_HOST')
API_NOTIFICATIONS_PORT = int(os.getenv('API_NOTIFICATIONS_PORT'))

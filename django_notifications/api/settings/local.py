from .base import *

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware", ]
INTERNAL_IPS = ['localhost', '127.0.0.1', '0.0.0.0']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda _request: True
}

SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
ADMIN_URL = os.environ.get("ADMIN_URL")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': int(os.environ.get('POSTGRES_PORT')),
        'OPTIONS': {
            'options': '-c search_path=public'
        },
        'ATOMIC_REQUESTS': True
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        },
    },
    'handlers': {
        'debug-console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'INFO',  # DEBUG if want to see all those sql requests...
            'handlers': ['debug-console'],
            'propagate': False,
        }
    },
}

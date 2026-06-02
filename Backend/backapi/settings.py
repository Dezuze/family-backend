from pathlib import Path
import os
import sys
import pymysql
from django.urls import reverse_lazy

pymysql.install_as_MySQLdb()

# Base directory (Backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass


# Security: Trust the 'X-Forwarded-Proto' header for determining SSL (Traefik handles this)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Import easy-thumbnails settings for django-image-cropping
from .thumbnail_settings import *

# Quick development settings - replace for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-prod')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'


def _csv_env(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


def _unique(values):
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


_domain = os.environ.get('DOMAIN', '').strip().rstrip('.')
_host_defaults = ['localhost', '127.0.0.1']
if _domain:
    _host_defaults.extend([
        _domain,
        f'www.{_domain}',
        f'api.{_domain}',
        f'www.api.{_domain}',
    ])

ALLOWED_HOSTS = _unique(_csv_env('DJANGO_ALLOWED_HOSTS', ','.join(_host_defaults)))
if 'test' in sys.argv:
    ALLOWED_HOSTS.append('testserver')

# SSL/HTTPS & Cookies
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = False # Handled by Traefik, but good to have if direct
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'easy_thumbnails',
    'image_cropping',
    'accounts',
    'families.apps.FamiliesConfig',
    'news',
    'profiles',
]

REST_FRAMEWORK = {
    # Use standard permission classes if needed default
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'backapi.middleware.media_cors.MediaCORSMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backapi.urls'

_cors_defaults = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://127.0.0.1:3001']
if _domain:
    _cors_defaults.extend([
        f'https://{_domain}',
        f'https://www.{_domain}',
        f'https://api.{_domain}',
        f'https://www.api.{_domain}',
    ])

CORS_ALLOWED_ORIGINS = _unique(_csv_env('CORS_ALLOWED_ORIGINS', ','.join(_cors_defaults)))
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
_csrf_defaults = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
if _domain:
    _csrf_defaults.extend([
        f'https://{_domain}',
        f'https://www.{_domain}',
        f'https://api.{_domain}',
        f'https://www.api.{_domain}',
    ])

CSRF_TRUSTED_ORIGINS = _unique(_csv_env('CSRF_TRUSTED_ORIGINS', ','.join(_csrf_defaults)))
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

_cookie_domain = os.environ.get('DJANGO_COOKIE_DOMAIN', '').strip()
if _cookie_domain:
    SESSION_COOKIE_DOMAIN = _cookie_domain
    CSRF_COOKIE_DOMAIN = _cookie_domain

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

WSGI_APPLICATION = 'backapi.wsgi.application'

if os.environ.get('DB_ENGINE') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
elif os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT', 5432),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }

REDIS_URL = os.environ.get('REDIS_URL', '').strip()
FAMILY_TREE_CACHE_TIMEOUT = int(os.environ.get('FAMILY_TREE_CACHE_TIMEOUT', 60 * 60 * 24 * 30))

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': os.environ.get('CACHE_KEY_PREFIX', 'family_site'),
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'family-site-dev',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'accounts.validators.ComplexPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []
_project_static_dir = BASE_DIR / "static"
if _project_static_dir.exists():
    STATICFILES_DIRS.append(_project_static_dir)
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging Configuration for Production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django_error.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Use the custom user model defined in the `accounts` app
AUTH_USER_MODEL = 'accounts.User'

UNFOLD = {
    "SITE_TITLE": "Kollamparambil Family Admin",
    "SITE_HEADER": "Kollamparambil Family",
    "SITE_SYMBOL": "family_restroom", # Material symbol
    "ENVIRONMENT": "backapi.utils.get_environment",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "243 245 242",
            "100": "227 232 225",
            "200": "202 213 199",
            "300": "166 185 162",
            "400": "124 150 118",
            "500": "91 118 86",
            "600": "70 92 66",
            "700": "57 74 54",
            "800": "45 58 43",  # Brand Olive Green
            "900": "40 50 38",
            "950": "21 27 20",
        },
        "accent": {
            "50": "251 248 241",
            "100": "244 236 219",
            "200": "233 215 181",
            "300": "218 189 134",
            "400": "199 155 91",
            "500": "166 141 91",  # Brand Gold
            "600": "150 117 75",
            "700": "125 95 63",
            "800": "102 78 56",
            "900": "84 65 47",
            "950": "45 33 24",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Authentication",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:accounts_user_changelist"),
                    },
                    {
                        "title": "Invite Tokens",
                        "icon": "vpn_key",
                        "link": reverse_lazy("admin:accounts_invitetoken_changelist"),
                    },
                ],
            },
            {
                "title": "Family Directory",
                "separator": True,
                "items": [
                    {
                        "title": "Families",
                        "icon": "family_restroom",
                        "link": reverse_lazy("admin:families_family_changelist"),
                    },
                    {
                        "title": "Members",
                        "icon": "group",
                        "link": reverse_lazy("admin:families_familymember_changelist"),
                    },
                    {
                        "title": "Deceased",
                        "icon": "hourglass_empty",
                        "link": reverse_lazy("admin:families_deceasedmember_changelist"),
                    },
                ],
            },
            {
                "title": "Content Management",
                "separator": True,
                "items": [
                    {
                        "title": "News & Events",
                        "icon": "newspaper",
                        "link": reverse_lazy("admin:news_post_changelist"),
                    },
                    {
                        "title": "Post Media",
                        "icon": "perm_media",
                        "link": reverse_lazy("admin:news_media_changelist"),
                    },
                ],
            },
            {
                "title": "Gallery & Committee",
                "separator": True,
                "items": [
                    {
                        "title": "Photo Gallery",
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:profiles_gallery_changelist"),
                    },
                    {
                        "title": "Committee (Records)",
                        "icon": "people",
                        "link": reverse_lazy("admin:families_familycommitteemember_changelist"),
                    },
                ],
            },
        ],
    },
}

"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from os import environ as env
from pathlib import Path

import dj_database_url

# points to our git repo's root
BASE_DIR = Path(
    env.get("DJANGO_BASE_DIR", str(Path(__file__).parent / ".." / ".." / ".."))
).resolve()

SECRET_KEY = env["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS: list[str] = []


# Application definition

INSTALLED_APPS = (
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    + [
        "whitenoise",
        "django_htmx",
        "axes",  # https://github.com/jazzband/django-axes
        "import_export",  # https://django-import-export.readthedocs.io/
    ]
    + [
        "apps.authentication",
        "apps.chess",
        "apps.daily_challenge",
        "apps.webui",
    ]
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
] + [
    "django_htmx.middleware.HtmxMiddleware",
    # "AxesMiddleware should be the last middleware in the MIDDLEWARE list"
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
    )
}


# Caches
# https://docs.djangoproject.com/en/5.1/topics/cache/
# https://docs.djangoproject.com/en/5.1/ref/settings/#std:setting-CACHES

CACHES = {
    "default": {
        # Let's kiss things simple for now, and let each Django worker
        # manage their own in-memory cache.
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Sessions
# https://docs.djangoproject.com/en/5.1/topics/http/sessions/#using-cookie-based-sessions

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# 6 months by default, so users can stop playing for a few months, come back, and see
# that they didn't lose their stats.
SESSION_COOKIE_AGE = int(env.get("SESSION_COOKIE_AGE", str(3600 * 24 * 30 * 6)))


#  Customizing authentication
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/

AUTH_USER_MODEL = "authentication.User"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "/admin"  # must match the Django Admin URL in urls.py


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Our custom settings:
ZAKUCHESS_VERSION = env.get("ZAKUCHESS_VERSION", "dev")
JS_CHESS_ENGINE = env.get("JS_CHESS_ENGINE", "stockfish")
MASTODON_PAGE = env.get("MASTODON_PAGE")
CANONICAL_URL = env.get("CANONICAL_URL", "https://zakuchess.com/")
DEBUG_LAYOUT = env.get("DEBUG_LAYOUT", "") == "1"

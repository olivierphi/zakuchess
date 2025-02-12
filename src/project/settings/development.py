from os import environ as env

from ._base import *

ALLOWED_HOSTS = ["*"]

DEBUG = True

INSTALLED_APPS += [
    "django_extensions",
]

USE_DJANGO_DEBUG_TOOLBAR = bool(env.get("USE_DJANGO_DEBUG_TOOLBAR"))
if USE_DJANGO_DEBUG_TOOLBAR and not IS_TESTING:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INTERNAL_IPS = ["127.0.0.1"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "uvicorn": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s [%(name)s] %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "uvicorn",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.get("DJANGO_LOG_LEVEL", default="WARNING"),
    },
    "loggers": {
        "apps": {
            "handlers": ["console"],
            "level": env.get("APP_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": env.get("SQL_LOG_LEVEL", default="WARNING"),
            "propagate": False,
        },
    },
}

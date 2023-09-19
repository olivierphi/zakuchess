from os import environ as env

from ._base import *

ALLOWED_HOSTS = ["*"]

DEBUG = True

INSTALLED_APPS += [
    "django_extensions",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
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

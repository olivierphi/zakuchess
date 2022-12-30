import os

os.environ["USE_DOT_ENV"] = "YES"

from ._base import *

ALLOWED_HOSTS = ["*"]

DEBUG = True

NO_HTTP_CACHE = True  # disable HTTP caching for development

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
        "level": env.str("DJANGO_LOG_LEVEL", default="WARNING"),
    },
    "loggers": {
        "apps": {
            "handlers": ["console"],
            "level": env.str("APP_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": env.str("SQL_LOG_LEVEL", default="WARNING"),
            "propagate": False,
        },
    },
}

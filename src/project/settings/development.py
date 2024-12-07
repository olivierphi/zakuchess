from os import environ as env

from ._base import *

ALLOWED_HOSTS = ["*"]

DEBUG = True

INSTALLED_APPS.insert(
    # Make sure `runserver` doesn't try to serve static assets,
    # even without the `--no-static` option:
    # (https://whitenoise.readthedocs.io/en/stable/django.html#using-whitenoise-in-development)
    INSTALLED_APPS.index("django.contrib.staticfiles"),
    "whitenoise.runserver_nostatic",
)

INSTALLED_APPS += [
    "django_extensions",
]

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

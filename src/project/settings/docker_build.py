from os import environ as env

env["SECRET_KEY"] = "does-not-matter-in-this-context"
env["DATABASE_URL"] = "sqlite://:memory:"
env["ALLOWED_HOSTS"] = "none"

from ._base import *

# Static assets served by Whitenoise on production
# @link http://whitenoise.evans.io/en/stable/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
        "level": "WARNING",
    },
}

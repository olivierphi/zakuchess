from ._base import *

ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")

SECURE_SSL_REDIRECT = bool(env.get("SECURE_SSL_REDIRECT", "1"))
if "CSRF_TRUSTED_ORIGINS" in env:
    CSRF_TRUSTED_ORIGINS = env["CSRF_TRUSTED_ORIGINS"].split(",")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
}


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

from ._base import *

ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")

SECURE_SSL_REDIRECT = bool(env.get("SECURE_SSL_REDIRECT", "1"))
if "CSRF_TRUSTED_ORIGINS" in env:
    CSRF_TRUSTED_ORIGINS = env["CSRF_TRUSTED_ORIGINS"].split(",")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Static assets served by Whitenoise on production
# @link http://whitenoise.evans.io/en/stable/
# > The WhiteNoise middleware should be placed directly after the
# > Django SecurityMiddleware and before all other middleware
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
}

# Logging
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

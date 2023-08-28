from ._base import *

ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")

SECURE_SSL_REDIRECT = bool(env.get("SECURE_SSL_REDIRECT", "1"))
CSRF_TRUSTED_ORIGINS = env.get("CSRF_TRUSTED_ORIGINS", "").split(",")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Static assets served by Whitenoise on production
# @link http://whitenoise.evans.io/en/stable/
MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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

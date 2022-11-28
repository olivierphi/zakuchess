from ._base import *

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

STATIC_ROOT = "/vercel/path0/static/"

DATABASES = {}

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

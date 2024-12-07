from .production import *

USE_X_FORWARDED_HOST = True  # Fly.io always sends request through a proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# @link https://django-axes.readthedocs.io/en/latest/4_configuration.html#configuring-reverse-proxies
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]

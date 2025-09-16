import os
from ._base import *

DEBUG = True

# https://docs.djangoproject.com/en/5.2/ref/django-admin/#envvar-DJANGO_RUNSERVER_HIDE_WARNING
os.environ["DJANGO_RUNSERVER_HIDE_WARNING"] = "true"

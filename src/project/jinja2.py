import urllib.parse
import uuid

from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from django_htmx.jinja import django_htmx_script
from jinja2 import Environment, StrictUndefined


def environment(**options) -> Environment:
    options["undefined"] = StrictUndefined
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "uuid": uuid.uuid4,
            "django_htmx_script": django_htmx_script,
        }
    )
    env.filters["date"] = defaultfilters.date
    env.filters["to_query_string"] = urllib.parse.urlencode

    return env

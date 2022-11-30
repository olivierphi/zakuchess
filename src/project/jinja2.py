import uuid
from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def environment(**options) -> Environment:
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "uuid": uuid.uuid4,
        }
    )
    env.filters["date"] = defaultfilters.date

    from apps.webui import jinja_extensions as webui_jinja_extensions

    env.filters |= webui_jinja_extensions.filters

    return env

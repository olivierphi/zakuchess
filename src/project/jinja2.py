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
        }
    )
    env.filters["date"] = defaultfilters.date

    from apps.webui import jinja_extensions as webui_jinja_extensions

    for filter_name, filter_implementation in webui_jinja_extensions.filters.items():
        env.filters[filter_name] = filter_implementation

    return env

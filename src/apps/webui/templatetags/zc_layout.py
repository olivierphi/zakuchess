from __future__ import annotations

import datetime as dt
import json
from typing import TYPE_CHECKING

from django import template
from django.conf import settings
from django.template.backends.utils import get_token as get_csrf_token

if TYPE_CHECKING:
    from django.http import HttpRequest

register = template.Library()


@register.simple_tag(takes_context=True)
def htmx_csrf(context: dict) -> str:
    request: HttpRequest | None = context.get("request")
    return json.dumps(
        {"X-CSRFToken": get_csrf_token(request) if request else "[no request]"}
    )


@register.simple_tag
def current_year() -> int:
    return dt.datetime.now().year


@register.simple_tag
def zakuchess_version() -> str:
    return settings.ZAKUCHESS_VERSION

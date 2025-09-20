from __future__ import annotations

import datetime as dt
import json
from typing import TYPE_CHECKING

from django import template
from django.conf import settings
from django.template.backends.utils import get_token as get_csrf_token
from django.templatetags.static import static

from .. import assets_generation

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
def generated_asset_static(asset_id: str) -> str:
    match asset_id:
        case "pico_css":
            assets_generation.download_pico_css_if_needed()
            return static(assets_generation.get_pico_css_filename())
        case _:
            raise ValueError(f"Unknown asset ID: {asset_id}")


@register.simple_tag
def current_year() -> int:
    return dt.datetime.now().year


@register.simple_tag
def zakuchess_version() -> str:
    return settings.ZAKUCHESS_VERSION

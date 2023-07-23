import json
from collections.abc import Sequence
from typing import TYPE_CHECKING

from django.template.backends.utils import get_token  # type: ignore[attr-defined]
from django.templatetags.static import static
from dominate.tags import (
    body,
    dom_tag,
    h1,
    h2,
    head as base_head,
    header as base_header,
    html,
    link,
    meta,
    script,
    style,
    title as base_title,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

# We'll do something cleaner later
# TODO: compress these fonts in woff2, and put them in "webui/static/webui/fonts".
_FONTS_CSS = """
@font-face {
  font-family: 'OpenSans';
  src: url('/static/webui/fonts/OpenSans.ttf') format('truetype');
}
@font-face {
  font-family: 'PixelFont';
  src: url('/static/webui/fonts/fibberish.ttf') format('truetype');
}
"""


def page(*, children: Sequence[dom_tag], request: "HttpRequest", title: str = "ZakuChess ♞") -> str:
    return f"<!DOCTYPE html>{document(children=children, request=request, title=title)}"


def document(*, children: Sequence[dom_tag], request: "HttpRequest", title: str = "ZakuChess ♞") -> dom_tag:
    return html(
        head(title=title),
        body(
            header(),
            *children,
            cls="bg-slate-900",
            data_hx_headers=json.dumps({"X-CSRFToken": get_token(request) if request else "[no request]"}),
        ),
    )


def head(*, title: str) -> dom_tag:
    return base_head(
        meta(charset="utf-8"),
        base_title(title),
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        meta(name="description", content="ZakuChess"),
        meta(name="keywords", content="chess roleplay"),
        style(_FONTS_CSS),
        link(rel="stylesheet", href=static("webui/css/tailwind.css")),
        script(src=static("webui/js/main.js")),
        script(src=static("chess/js/chess-main.js")),
    )


def header() -> dom_tag:
    return base_header(
        h1(
            "Zakuchess",
            cls="text-slate-50 text-2xl leading-none font-pixel",
        ),
        h2(
            "Chess with character(s)",
            cls="text-slate-50 text-xl leading-none font-pixel",
        ),
        cls="text-center md:mx-auto md:max-w-2xl",
    )

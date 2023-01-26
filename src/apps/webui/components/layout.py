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
    title as base_title,
)

if TYPE_CHECKING:
    from django.http import HttpRequest


def page(*, children: Sequence[dom_tag], request: "HttpRequest", title: str = "ZakuChess ♞") -> str:
    return f"<!DOCTYPE html>{document(children=children, request=request, title=title)}"


def document(*, children: Sequence[dom_tag], request: "HttpRequest", title: str = "ZakuChess ♞") -> dom_tag:
    return html(
        head(title=title),
        body(
            header(),
            *children,
            cls="bg-slate-800",
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
        link(rel="stylesheet", href=static("webui/css/tailwind.css")),
        link(rel="stylesheet", href=static("webui/css/main.css")),
        script(src=static("webui/js/main.js")),
        script(src=static("chess/js/chess-main.js")),
    )


def header() -> dom_tag:
    return base_header(
        h1(
            "Zakuchess",
            cls="text-slate-50 text-2xl font-pixel",
        ),
        h2(
            "Chess with character(s)",
            cls="text-slate-50 text-xl font-pixel",
        ),
        cls="text-center md:mx-auto md:max-w-2xl",
    )

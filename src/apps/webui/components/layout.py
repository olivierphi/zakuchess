import base64
import json
from functools import cache
from typing import TYPE_CHECKING

from django.conf import settings
from django.template.backends.utils import get_token  # type: ignore[attr-defined]
from django.templatetags.static import static
from dominate.tags import (
    a,
    body,
    div,
    footer as base_footer,
    h1,
    h2,
    head as base_head,
    header as base_header,
    html,
    img,
    link,
    meta,
    script,
    style,
    title as base_title,
)
from dominate.util import raw

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag
    from dominate.util import text

# We'll do something cleaner later
# TODO: compress these fonts in woff2, and put them in "webui/static/webui/fonts".
_FONTS_CSS = """
@font-face {
  font-family: 'OpenSans';
  src: url('/static/webui/fonts/OpenSans.woff2') format('woff2');
}
@font-face {
  font-family: 'PixelFont';
  src: url('/static/webui/fonts/fibberish.ttf') format('truetype');
}
"""


def page(
    *children: "dom_tag", request: "HttpRequest", title: str = "ZakuChess ♞"
) -> str:
    return f"<!DOCTYPE html>{document(*children, request=request, title=title)}"


def document(
    *children: "dom_tag", request: "HttpRequest", title: str = "ZakuChess ♞"
) -> "dom_tag":
    return html(
        head(title=title),
        body(
            header(),
            *children,
            footer(),
            cls="bg-slate-900",
            data_hx_headers=json.dumps(
                {"X-CSRFToken": get_token(request) if request else "[no request]"}
            ),
        ),
        __pretty=settings.DEBUG,
    )


def head(*, title: str) -> "dom_tag":
    return base_head(
        meta(charset="utf-8"),
        base_title(title),
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        meta(name="description", content="ZakuChess"),
        meta(name="keywords", content="chess roleplay"),
        link(
            rel="icon",
            type="image/png",
            sizes="16x16",
            href=static("webui/img/favicon-16x16.png"),
        ),
        link(
            rel="icon",
            type="image/png",
            sizes="32x32",
            href=static("webui/img/favicon-32x32.png"),
        ),
        style(_FONTS_CSS),
        link(rel="stylesheet", href=static("webui/css/tailwind.css")),
        script(src=static("webui/js/main.js")),
        script(src=static("chess/js/chess-main.js")),
    )


def header() -> "dom_tag":
    return base_header(
        h1(
            "ZakuChess",
            cls="text-slate-50 text-2xl leading-none font-pixel",
        ),
        h2(
            "Chess with character(s)",
            cls="text-slate-50 text-xl leading-none font-pixel",
        ),
        cls="text-center md:mx-auto md:max-w-2xl",
    )


@cache
def footer() -> "text":
    GITHUB_SVG = b"""<svg width="98" height="96" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z" fill="#fff"/></svg>"""
    svg_b64 = base64.b64encode(GITHUB_SVG).decode("utf-8")

    common_links_attributes = {
        "rel": "noreferrer noopener",
        "target": "_blank",
        "cls": "underline hover:no-underline",
    }

    return raw(
        base_footer(
            div(
                "Made with ❤️ in 🏴󠁧󠁢󠁳󠁣󠁴󠁿",
                cls="text-center",
            ),
            div("© 2023 ZakuChess", cls="text-center mb-3"),
            div(
                "This website is open source. ",
                a(
                    img(
                        src=f"data:image/svg+xml;base64,{svg_b64}",
                        cls="inline-block w-4 aspect-square",
                        alt="GitHub logo",
                    ),
                    href="https://github.com/olivierphi/zakuchess",
                    **common_links_attributes,
                ),
                cls="align-middle",
            ),
            div(
                a(
                    f"Version {settings.ZAKUCHESS_VERSION}",
                    href="https://github.com/olivierphi/zakuchess",
                    **common_links_attributes,
                ),
            ),
            cls="w-full text-slate-100 text-sm text-center mb-10 md:max-w-xl mx-auto",
        ).render(pretty=settings.DEBUG)
    )

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
    from collections.abc import Sequence

    from django.http import HttpRequest
    from dominate.tags import dom_tag
    from dominate.util import text

# We'll do something cleaner later
# TODO: subset the OpenSans font, once we have extracted text in i18n files.
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


_META_TITLE = "ZakuChess ♞ - A daily chess challenge with pixel art units"
_META_DESCRIPTION = (
    """Play chess with character(s) - """
    """a chess game with pixel art units, with a new challenge each day."""
)
_DOCUMENT_BG_COLOR = "bg-body-background"


def page(
    *children: "dom_tag",
    request: "HttpRequest",
    title: str = _META_TITLE,
    left_side_buttons: "list[dom_tag] | None" = None,
    right_side_buttons: "list[dom_tag] | None" = None,
    head_children: "Sequence[dom_tag] | None" = None,
) -> str:
    return "<!DOCTYPE html>" + str(
        document(
            *children,
            request=request,
            left_side_buttons=left_side_buttons,
            right_side_buttons=right_side_buttons,
            head_children=head_children,
            title=title,
        )
    )


def document(
    *children: "dom_tag",
    request: "HttpRequest",
    title: str,
    left_side_buttons: "list[dom_tag] | None",
    right_side_buttons: "list[dom_tag] | None" = None,
    head_children: "Sequence[dom_tag] | None" = None,
) -> "dom_tag":
    return html(
        head(*(head_children or []), title=title),
        body(
            header(
                left_side_buttons=left_side_buttons,
                right_side_buttons=right_side_buttons,
            ),
            *children,
            footer(),
            modals_container(),
            cls=_DOCUMENT_BG_COLOR,
            data_hx_headers=json.dumps(
                {"X-CSRFToken": get_token(request) if request else "[no request]"}
            ),
            data_hx_ext="class-tools",  # enable CSS class transitions on the whole page
        ),
        lang="en",  # hopefully we'll have i18n one day :-)
        prefix="og: https://ogp.me/ns#",  # Open Graph Protocol
        __pretty=settings.DEBUG,
    )


def head(*children: "dom_tag", title: str) -> "dom_tag":
    return base_head(
        meta(charset="utf-8"),
        base_title(title),
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        meta(name="description", content=_META_DESCRIPTION),
        meta(name="keywords", content="chess pixel-art roleplay"),
        link(rel="canonical", href=settings.CANONICAL_URL),
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
        link(rel="stylesheet", href=static("webui/css/zakuchess.css")),
        script(src=static("webui/js/main.js")),
        script(src=static("chess/js/chess-main.js")),
        # @link https://ogp.me/
        meta(property="og:title", content=title),
        meta(property="og:description", content=_META_DESCRIPTION),
        # @link https://ogp.me/#types
        meta(property="og:type", content="website"),
        *(
            link(rel="me", href=settings.MASTODON_PAGE)
            if settings.MASTODON_PAGE
            else []
        ),
        *children,
    )


def header(
    *,
    left_side_buttons: "list[dom_tag] | None",
    right_side_buttons: "list[dom_tag] | None" = None,
) -> "dom_tag":
    def side_wrapper(*children: "dom_tag", align: str) -> "dom_tag":
        return div(
            *children,
            cls=f"flex w-1/6 {align}",
        )

    return base_header(
        div(
            side_wrapper(*(left_side_buttons or []), align="justify-start"),
            div(
                h1(
                    "ZakuChess",
                    cls="text-slate-50 text-2xl leading-none font-pixel",
                ),
                h2(
                    "Chess with character(s)",
                    cls="text-slate-50 text-xl leading-none font-pixel",
                ),
                cls="grow text-center md:mx-auto md:max-w-2xl",
            ),
            side_wrapper(*(right_side_buttons or []), align="justify-end"),
            cls="flex items-center p-2 w-full mx-auto md:max-w-3xl xl:max-w-7xl",
        ),
        cls="bg-gray-950",
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

    # TODO: manage i18n
    return raw(
        base_footer(
            div(
                "Made with ❤️ in 🏴󠁧󠁢󠁳󠁣󠁴󠁿",
                cls="text-center",
            ),
            div("© 2023-2024 ZakuChess", cls="text-center mb-3"),
            div(
                "This web game is open source. ",
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
            cls="w-full text-slate-100 text-sm text-center mt-1 mb-10 md:max-w-xl mx-auto",
        ).render(pretty=settings.DEBUG)
    )


@cache
def modals_container() -> "text":
    return raw(
        div(
            script(
                raw(
                    r"""
                function closeModal() { 
                    const modal = document.getElementById("modals-container")
                    modal.innerHTML = ""
                    modal.className = "hidden"
                }
                """
                )
            ),
            div(
                id="modals-container",
                cls="hidden",
            ),
        ).render(pretty=settings.DEBUG)
    )

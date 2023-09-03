from functools import cache

from django.conf import settings
from dominate.tags import a, div, dom_tag, footer as footer_tag, span
from dominate.util import raw


@cache
def footer() -> dom_tag:
    common_links_attributes = {
        "rel": "noreferrer noopener",
        "target": "_blank",
        "cls": "underline hover:no-underline",
    }

    return raw(
        footer_tag(
            div(
                "Made with ❤️ by ",
                a("oliphi", href="https://github.com/olivierphi", **common_links_attributes),
                ".",
                cls="text-center",
            ),
            div("© 2023 ZakuChess", cls="text-center mb-3"),
            span(
                "This website is open source. Version ",
                a(
                    settings.ZAKUCHESS_VERSION,
                    href="https://github.com/olivierphi/zakuchess",
                    **common_links_attributes,
                ),
            ),
            cls="w-full text-slate-100 text-sm text-center mb-10 md:max-w-xl mx-auto",
        ).render(pretty=settings.DEBUG)
    )

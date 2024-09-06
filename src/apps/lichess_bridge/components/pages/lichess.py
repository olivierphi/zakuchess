from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import button, div, form, p, section

from apps.webui.components import common_styles
from apps.webui.components.forms_common import csrf_hidden_input
from apps.webui.components.layout import page

from ... import lichess_api
from ..misc_ui import detach_lichess_account_form
from ..svg_icons import ICON_SVG_LOG_IN

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ...models import LichessAccessToken


def lichess_no_account_linked_page(
    *,
    request: "HttpRequest",
) -> str:
    return page(
        section(
            form(
                csrf_hidden_input(request),
                p("Click here to log in to Lichess"),
                button(
                    "Log in via Lichess",
                    " ",
                    ICON_SVG_LOG_IN,
                    type="submit",
                    cls=common_styles.BUTTON_CLASSES,
                ),
                action=reverse("lichess_bridge:oauth2_start_flow"),
                method="POST",
            ),
            cls="text-slate-50",
        ),
        request=request,
        title="Lichess - no account linked",
    )


async def lichess_account_linked_homepage(
    *,
    request: "HttpRequest",
    access_token: "LichessAccessToken",
) -> str:
    me = await lichess_api.get_lichess_my_account(access_token)

    return page(
        div(
            section(
                f'Hello {me["username"]}!',
                cls="text-slate-50",
            ),
            div(
                detach_lichess_account_form(request),
                cls="mt-4",
            ),
            cls="w-full mx-auto bg-slate-900 min-h-48 "
            "md:max-w-3xl xl:max-w-7xl xl:border xl:rounded-md xl:border-neutral-800",
        ),
        request=request,
        title="Lichess - account linked",
    )

from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import button, div, form, h3, h4, p, span

from apps.chess.components.misc_ui import modal_container
from apps.webui.components import common_styles
from apps.webui.components.forms_common import csrf_hidden_input

from ..svg_icons import ICON_SVG_LOG_OUT, ICON_SVG_USER

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag

    from apps.lichess_bridge.models import LichessAccountInformation


def user_profile_modal(
    *, request: "HttpRequest", me: "LichessAccountInformation"
) -> "dom_tag":
    return modal_container(
        header=h3(
            "Lichess account ",
            ICON_SVG_USER,
            cls="text-xl",
        ),
        body=div(
            _user_profile_form(request, me),
            cls="p-6 space-y-6",
        ),
    )


def _user_profile_form(request: "HttpRequest", me: "LichessAccountInformation") -> form:
    spacing = "mb-3"

    return form(
        csrf_hidden_input(request),
        h4(
            "Your Lichess account '",
            span(me.username, cls="text-yellow-400"),
            "' is connected to ZakuChess.",
            cls=f"{spacing} text-center font-bold ",
        ),
        p(
            "ZakuChess doesn't store anything related to your Lichess account: "
            "this connection only exists in your web browser.",
            cls=f"{spacing} text-center",
        ),
        p(
            "If you want to disconnect your Lichess account from Zakuchess, ",
            "Use the following button:",
            cls=f"{spacing} text-center",
        ),
        p(
            button(
                "Disconnect Lichess account",
                " ",
                ICON_SVG_LOG_OUT,
                type="submit",
                cls=common_styles.BUTTON_CANCEL_CLASSES,
            ),
            cls=f"{spacing} text-center",
        ),
        p("You can always reconnect it later 🙂", cls=f"{spacing} text-center"),
        action=reverse("lichess_bridge:detach_lichess_account"),
        method="POST",
    )

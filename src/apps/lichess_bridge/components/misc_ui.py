from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import button, form

from apps.webui.components import common_styles
from apps.webui.components.forms_common import csrf_hidden_input

from .svg_icons import ICON_SVG_LOG_OUT

if TYPE_CHECKING:
    from django.http import HttpRequest


def detach_lichess_account_form(request: "HttpRequest") -> form:
    return form(
        csrf_hidden_input(request),
        button(
            "Log out from Lichess",
            " ",
            ICON_SVG_LOG_OUT,
            cls=common_styles.BUTTON_CLASSES,
        ),
        action=reverse("lichess_bridge:detach_lichess_account"),
        method="POST",
    )

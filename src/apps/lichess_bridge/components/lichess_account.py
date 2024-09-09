from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import button, div, form, p

from apps.webui.components.forms_common import csrf_hidden_input

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import html_tag


def lichess_linked_account_inner_footer(request: "HttpRequest") -> "html_tag":
    return div(
        detach_lichess_account_form(request),
        cls="my-4",
    )


def detach_lichess_account_form(request: "HttpRequest") -> form:
    return form(
        csrf_hidden_input(request),
        p(
            "You can disconnect your Lichess account from Zakuchess at any time.",
            cls="text-center",
        ),
        p(
            "Tap ",
            button(
                "here",
                type="submit",
                cls="text-rose-600 underline",
            ),
            " to disconnect it.",
            cls="text-center",
        ),
        p("(you can always reconnect it later)", cls="text-center"),
        action=reverse("lichess_bridge:detach_lichess_account"),
        method="POST",
        cls="mt-16 text-slate-50 text-sm",
    )

from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import b, br, button, div, form, p

from apps.chess.models import GameFactions
from apps.lichess_bridge.components.svg_icons import ICON_SVG_LOG_IN
from apps.webui.components import common_styles
from apps.webui.components.chess_units import unit_display_container
from apps.webui.components.forms_common import csrf_hidden_input

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag

_SHOWN_UNITS_FACTIONS = GameFactions(w="humans", b="undeads")


def no_linked_account_content(request: "HttpRequest") -> "dom_tag":
    return div(
        p(
            "You can play games with your friends and other people all around the world on ZakuChess, "
            "by linking your Lichess account.",
            cls="mb-4 text-center",
        ),
        p(
            "This will allow you to play Lichess games via ZakuChess' boards, "
            "where chess pieces are played by pixel art characters 🙂",
            cls="mb-4 text-center",
        ),
        div(
            unit_display_container(
                piece_role="K", factions=_SHOWN_UNITS_FACTIONS, row_counter=0
            ),
            unit_display_container(
                piece_role="Q", factions=_SHOWN_UNITS_FACTIONS, row_counter=1
            ),
            unit_display_container(
                piece_role="N1",
                factions=_SHOWN_UNITS_FACTIONS,
                row_counter=0,
                # We don't have enough space on small screens to display all the units
                additional_classes="hidden md:block",
            ),
            div("VS", cls="grow px-4 text-center"),
            unit_display_container(
                piece_role="n1",
                factions=_SHOWN_UNITS_FACTIONS,
                row_counter=0,
                # ditto
                additional_classes="hidden md:block",
            ),
            unit_display_container(
                piece_role="q", factions=_SHOWN_UNITS_FACTIONS, row_counter=1
            ),
            unit_display_container(
                piece_role="k", factions=_SHOWN_UNITS_FACTIONS, row_counter=0
            ),
            cls="flex justify-center items-center gap-1 md:gap-3",
        ),
        form(
            csrf_hidden_input(request),
            p(
                b("Click here to log in to Lichess"),
                cls="mb-4 text-center font-bold",
            ),
            p(
                button(
                    "Log in via Lichess",
                    " ",
                    ICON_SVG_LOG_IN,
                    type="submit",
                    cls=common_styles.BUTTON_CLASSES,
                ),
                cls="mb-4 text-center",
            ),
            action=reverse("lichess_bridge:oauth2_start_flow"),
            method="POST",
            cls="my-8",
        ),
        p(
            "You will be able to disconnect your Lichess account from ZakuChess at any time.",
            br(),
            b(
                "None of your Lichess data is stored on our end: it is only stored in your web browser."
            ),
            cls="mt-8 text-center text-sm",
        ),
    )

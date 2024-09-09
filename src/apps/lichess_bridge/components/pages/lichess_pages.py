from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import (
    a,
    b,
    button,
    div,
    fieldset,
    form,
    h3,
    input_,
    label,
    legend,
    p,
    section,
)

from apps.chess.components.chess_board import chess_arena
from apps.webui.components import common_styles
from apps.webui.components.forms_common import csrf_hidden_input
from apps.webui.components.layout import page

from ...models import LichessCorrespondenceGameDaysChoice
from ...presenters import LichessCorrespondenceGamePresenter
from ..lichess_account import (
    detach_lichess_account_form,
    lichess_linked_account_inner_footer,
)
from ..ongoing_games import lichess_ongoing_games
from ..svg_icons import ICON_SVG_CREATE, ICON_SVG_LOG_IN

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ...models import (
        LichessAccountInformation,
        LichessGameExport,
        LichessOngoingGameData,
    )


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


def lichess_account_linked_homepage(
    *,
    request: "HttpRequest",
    me: "LichessAccountInformation",
    ongoing_games: "list[LichessOngoingGameData]",
) -> str:
    return page(
        div(
            section(
                h3(
                    "Logged in as ",
                    b(f"{me.username}@Lichess", cls="text-yellow-400 font-bold"),
                    cls="mb-2 border rounded-t-md border-slate-700 bg-slate-800 text-lg text-center",
                ),
                lichess_ongoing_games(ongoing_games),
                p(
                    a(
                        "Create a new game",
                        href=reverse("lichess_bridge:create_game"),
                        cls=common_styles.BUTTON_CLASSES,
                    ),
                ),
                cls="text-center text-slate-50",
            ),
            lichess_linked_account_inner_footer(request),
            cls="w-full mx-auto bg-slate-900 min-h-48 pb-4 "
            " md:max-w-3xl xl:max-w-7xl xl:border xl:rounded-md xl:border-neutral-800",
        ),
        request=request,
        title="Lichess - account linked",
    )


def lichess_correspondence_game_creation_page(
    request: "HttpRequest", form_errors: dict
) -> str:
    return page(
        div(
            section(
                form(
                    csrf_hidden_input(request),
                    div(
                        fieldset(
                            legend("Days per turn."),
                            (
                                p(form_errors["days_per_turn"], cls="text-red-600 ")
                                if "days_per_turn" in form_errors
                                else ""
                            ),
                            div(
                                *[
                                    div(
                                        input_(
                                            id=f"days-per-turn-{value}",
                                            type="radio",
                                            name="days_per_turn",
                                            value=value,
                                            checked=(
                                                value
                                                == LichessCorrespondenceGameDaysChoice.THREE_DAYS.value  # type: ignore[attr-defined]
                                            ),
                                        ),
                                        label(
                                            display, html_for=f"days-per-turn-{value}"
                                        ),
                                    )
                                    for value, display in LichessCorrespondenceGameDaysChoice.choices
                                ],
                                cls="flex gap-3",
                            ),
                            cls="block text-sm font-bold mb-2",
                        ),
                        input_(
                            id="days-per-turn",
                            cls="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                        ),
                        cls="mb-4",
                    ),
                    button(
                        "Create",
                        " ",
                        ICON_SVG_CREATE,
                        type="submit",
                        cls=common_styles.BUTTON_CLASSES,
                    ),
                    action=reverse("lichess_bridge:create_game"),
                    method="POST",
                ),
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
        title="Lichess - new correspondence game",
    )


def lichess_correspondence_game_page(
    *,
    request: "HttpRequest",
    me: "LichessAccountInformation",
    game_data: "LichessGameExport",
) -> str:
    game_presenter = LichessCorrespondenceGamePresenter(game_data, my_player_id=me.id)

    return page(
        chess_arena(
            game_presenter=game_presenter,
            status_bars=[],
            board_id="main",
        ),
        request=request,
        title=f"Lichess - correspondence game {game_data.id}",
    )

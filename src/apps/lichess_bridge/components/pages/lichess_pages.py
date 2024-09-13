from typing import TYPE_CHECKING, TypedDict

from django.conf import settings
from django.urls import reverse
from dominate.tags import (
    a,
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
    span,
)

from apps.chess.components.chess_board import (
    chess_arena,
    chess_available_targets,
    chess_last_move,
    chess_pieces,
)
from apps.chess.components.misc_ui import speech_bubble_container
from apps.webui.components import common_styles
from apps.webui.components.forms_common import csrf_hidden_input
from apps.webui.components.layout import page
from apps.webui.components.misc_ui.header import header_button
from apps.webui.components.misc_ui.user_prefs_modal import user_prefs_button

from ...models import LichessCorrespondenceGameDaysChoice
from ..ongoing_games import lichess_ongoing_games
from ..svg_icons import ICON_SVG_CREATE, ICON_SVG_LOG_IN, ICON_SVG_USER

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag

    from ...models import (
        LichessAccountInformation,
        LichessOngoingGameData,
    )
    from ...presenters import LichessCorrespondenceGamePresenter


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
        **_get_page_header_buttons(lichess_profile_linked=False),
    )


def lichess_my_current_games_list_page(
    *,
    request: "HttpRequest",
    me: "LichessAccountInformation",
    ongoing_games: "list[LichessOngoingGameData]",
) -> str:
    return page(
        div(
            section(
                h3(
                    "Your ongoing games on Lichess",
                    cls="text-slate-50 font-bold text-center",
                ),
                lichess_ongoing_games(ongoing_games),
                p(
                    a(
                        "Create a new game",
                        href=reverse("lichess_bridge:create_game"),
                        cls=common_styles.BUTTON_CLASSES,
                    ),
                    cls="my-8 text-center text-slate-50",
                ),
            ),
            _lichess_account_footer(me),
            cls="w-full mx-auto bg-slate-900 min-h-48 pb-4 md:max-w-3xl",
        ),
        request=request,
        title="Lichess - account linked",
        **_get_page_header_buttons(lichess_profile_linked=True),
    )


def lichess_correspondence_game_creation_page(
    request: "HttpRequest", *, me: "LichessAccountInformation", form_errors: dict
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
                _lichess_account_footer(me),
                cls="text-slate-50",
            ),
            cls="w-full mx-auto bg-slate-900 min-h-48 md:max-w-3xl",
        ),
        request=request,
        title="Lichess - new correspondence game",
        **_get_page_header_buttons(lichess_profile_linked=True),
    )


def lichess_correspondence_game_page(
    *,
    request: "HttpRequest",
    me: "LichessAccountInformation",
    game_presenter: "LichessCorrespondenceGamePresenter",
) -> str:
    return page(
        chess_arena(
            game_presenter=game_presenter,
            status_bars=[],
            board_id="main",
        ),
        _lichess_account_footer(me),
        request=request,
        title=f"Lichess - correspondence game {game_presenter.game_id}",
        **_get_page_header_buttons(lichess_profile_linked=True),
    )


def lichess_game_moving_parts_fragment(
    *,
    game_presenter: "LichessCorrespondenceGamePresenter",
    request: "HttpRequest",
    board_id: str,
) -> str:
    return "\n".join(
        (
            dom_tag.render(pretty=settings.DEBUG)
            for dom_tag in (
                chess_pieces(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
                chess_available_targets(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                (
                    chess_last_move(
                        game_presenter=game_presenter,
                        board_id=board_id,
                        data_hx_swap_oob="outerHTML",
                    )
                    if game_presenter.refresh_last_move
                    else div("")
                ),
                div(
                    speech_bubble_container(
                        game_presenter=game_presenter,
                        board_id=board_id,
                    ),
                    id=f"chess-speech-container-{board_id}",
                    data_hx_swap_oob="innerHTML",
                ),
            )
        )
    )


def _lichess_account_footer(me: "LichessAccountInformation") -> "dom_tag":
    return p(
        "Your Lichess account: ",
        span(me.username, cls="text-yellow-400"),
        cls="mt-8 mb-4 text-slate-50 text-center text-sm",
    )


class _PageHeaderButtons(TypedDict):
    left_side_buttons: list["dom_tag"]
    right_side_buttons: list["dom_tag"]


def _get_page_header_buttons(lichess_profile_linked: bool) -> _PageHeaderButtons:
    return _PageHeaderButtons(
        left_side_buttons=[_user_account_button()] if lichess_profile_linked else [],
        right_side_buttons=[user_prefs_button()],
    )


def _user_account_button() -> "dom_tag":
    htmx_attributes = {
        "data_hx_get": reverse("lichess_bridge:htmx_modal_user_account"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "outerHTML",
    }

    return header_button(
        icon=ICON_SVG_USER,
        title="Manage your Lichess account",
        id_="stats-button",
        htmx_attributes=htmx_attributes,
    )

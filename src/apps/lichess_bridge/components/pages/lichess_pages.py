from typing import TYPE_CHECKING, TypedDict

from django.conf import settings
from django.urls import reverse
from dominate.tags import (
    a,
    b,
    br,
    button,
    div,
    form,
    h3,
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
from apps.chess.models import GameFactions
from apps.webui.components import common_styles
from apps.webui.components.chess_units import (
    unit_display_container,
)
from apps.webui.components.forms_common import csrf_hidden_input
from apps.webui.components.layout import page
from apps.webui.components.misc_ui.header import header_button
from apps.webui.components.misc_ui.user_prefs_modal import user_prefs_button

from ..game_creation import game_creation_form
from ..ongoing_games import lichess_ongoing_games
from ..svg_icons import ICON_SVG_LOG_IN, ICON_SVG_USER

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag

    from ...models import (
        LichessAccountInformation,
        LichessOngoingGameData,
    )
    from ...presenters import LichessCorrespondenceGamePresenter

_PAGE_TITLE_CSS = "mb-8 text-center font-bold text-yellow-400"
_NON_GAME_PAGE_MAIN_SECTION_BASE_CSS = (
    "w-full mx-auto py-4 bg-slate-900 text-slate-50 min-h-48 md:max-w-3xl"
)
_NON_GAME_PAGE_SECTION_INNER_CONTAINER_CSS = "px-8 pb-8 md:px-0 md:w-8/12 md:mx-auto"


def lichess_no_account_linked_page(
    *,
    request: "HttpRequest",
) -> str:
    game_factions = GameFactions(w="humans", b="undeads")

    return page(
        section(
            div(
                h3(
                    "Play games on ZakuChess with your Lichess account",
                    cls=_PAGE_TITLE_CSS,
                ),
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
                        piece_role="K", factions=game_factions, row_counter=0
                    ),
                    unit_display_container(
                        piece_role="Q", factions=game_factions, row_counter=1
                    ),
                    unit_display_container(
                        piece_role="N1", factions=game_factions, row_counter=0
                    ),
                    div("VS", cls="grow px-4 text-center"),
                    unit_display_container(
                        piece_role="n1", factions=game_factions, row_counter=0
                    ),
                    unit_display_container(
                        piece_role="q", factions=game_factions, row_counter=1
                    ),
                    unit_display_container(
                        piece_role="k", factions=game_factions, row_counter=0
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
                cls=_NON_GAME_PAGE_SECTION_INNER_CONTAINER_CSS,
            ),
            cls=_NON_GAME_PAGE_MAIN_SECTION_BASE_CSS,
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
        section(
            div(
                h3(
                    "Your ongoing games on Lichess",
                    cls=_PAGE_TITLE_CSS,
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
                _lichess_account_footer(me),
                cls=_NON_GAME_PAGE_SECTION_INNER_CONTAINER_CSS,
            ),
            cls=_NON_GAME_PAGE_MAIN_SECTION_BASE_CSS,
        ),
        request=request,
        title="Lichess - account linked",
        **_get_page_header_buttons(lichess_profile_linked=True),
    )


def lichess_correspondence_game_creation_page(
    request: "HttpRequest",
    *,
    me: "LichessAccountInformation",
    form_errors: dict,
) -> str:
    return page(
        section(
            div(
                h3(
                    "New correspondence game, via Lichess",
                    cls=_PAGE_TITLE_CSS,
                ),
                game_creation_form(request=request, form_errors=form_errors),
                _lichess_account_footer(me),
                cls=_NON_GAME_PAGE_SECTION_INNER_CONTAINER_CSS,
            ),
            cls=_NON_GAME_PAGE_MAIN_SECTION_BASE_CSS,
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
    return div(
        p(
            "Your Lichess account: ",
            span(me.username, cls="text-yellow-400"),
            cls="w-9/12 mx-auto mt-8 mb-4 text-slate-50 text-center text-sm",
        ),
        p(
            "You can disconnect your Lichess account from ZakuChess at any time "
            "in your 'user account' ",
            ICON_SVG_USER,
            " settings, accessible from the top menu.",
            cls="w-9/12 mx-auto text-slate-50 text-center text-sm",
        ),
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

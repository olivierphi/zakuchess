from typing import TYPE_CHECKING

from django.conf import settings

from apps.webui.components.layout import page

from ..chess_board import (
    chess_arena,
    chess_available_targets,
    chess_daily_challenge_bar,
    chess_pieces,
    chess_status_bar,
)
from ..misc_ui.footer import footer

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ...presenters import GamePresenter

# These are the top-level components returned by our Django Views.


def chess_page(
    *, game_presenter: "GamePresenter", request: "HttpRequest", board_id: str
) -> str:
    return page(
        chess_arena(game_presenter=game_presenter, board_id=board_id),
        footer(),
        request=request,
    )


def chess_select_piece_htmx_fragment(
    *, game_presenter: "GamePresenter", request: "HttpRequest", board_id: str
) -> str:
    return "\n".join(
        (
            dom_tag.render(pretty=settings.DEBUG)
            for dom_tag in (
                chess_available_targets(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
                chess_pieces(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                chess_daily_challenge_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                chess_status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
            )
        )
    )


def chess_moving_parts_fragment(
    *, game_presenter: "GamePresenter", request: "HttpRequest", board_id: str
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
                    data_hx_swap_oob="innerHTML",
                ),
                chess_daily_challenge_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                chess_status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
            )
        )
    )

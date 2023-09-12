from typing import TYPE_CHECKING

from django.conf import settings

from apps.chess.components.chess_board import (
    chess_arena,
    chess_available_targets,
    chess_last_move,
    chess_pieces,
)
from apps.chess.components.misc_ui import speech_bubble_container
from apps.webui.components.layout import page

from ..misc_ui import daily_challenge_bar, status_bar

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ...presenters import DailyChallengeGamePresenter

# These are the top-level components returned by our Django Views.


def daily_challenge_page(
    *,
    game_presenter: "DailyChallengeGamePresenter",
    request: "HttpRequest",
    board_id: str,
) -> str:
    return page(
        chess_arena(
            game_presenter=game_presenter,
            board_id=board_id,
            status_bars=[
                daily_challenge_bar(game_presenter=game_presenter, board_id=board_id),
                status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
            ],
        ),
        request=request,
    )


def daily_challenge_moving_parts_fragment(
    *,
    game_presenter: "DailyChallengeGamePresenter",
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
                chess_last_move(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                daily_challenge_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                speech_bubble_container(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
            )
        )
    )

from typing import TYPE_CHECKING

from apps.webui.components.layout import page

from .. import chess

if TYPE_CHECKING:
    from django.http import HttpRequest

    from ...presenters import GamePresenter


def chess_page(*, game_presenter: "GamePresenter", request: "HttpRequest", board_id: str) -> str:
    return page(
        children=[
            chess.chess_arena(game_presenter=game_presenter, board_id=board_id),
        ],
        request=request,
    )


def chess_select_piece_htmx_fragment(*, game_presenter: "GamePresenter", request: "HttpRequest", board_id: str) -> str:
    return "\n".join(
        (
            dom_tag.render()
            for dom_tag in (
                chess.chess_available_targets(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
                chess.chess_pieces(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                chess.chess_daily_challenge_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                chess.chess_status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
            )
        )
    )


def chess_moving_parts_fragment(*, game_presenter: "GamePresenter", request: "HttpRequest", board_id: str) -> str:
    return "\n".join(
        (
            dom_tag.render()
            for dom_tag in (
                chess.chess_pieces(
                    game_presenter=game_presenter,
                    board_id=board_id,
                ),
                chess.chess_available_targets(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="innerHTML",
                ),
                chess.chess_daily_challenge_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
                chess.chess_status_bar(
                    game_presenter=game_presenter,
                    board_id=board_id,
                    data_hx_swap_oob="outerHTML",
                ),
            )
        )
    )

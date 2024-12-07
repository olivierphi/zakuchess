from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.urls import reverse
from dominate.tags import b, div, p

from apps.webui.components.molecules.chess_arena_companion_bars import (
    companion_bar,
    confirmation_dialog_bar,
)

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from ...presenters import LichessCorrespondenceGamePresenter


def lichess_bridge_bar(
    *,
    game_presenter: LichessCorrespondenceGamePresenter,
    board_id: str,
    htmx_attrs: dict[str, str] | None = None,
) -> dom_tag:
    if game_presenter.target_square_to_confirm is not None:
        return move_piece_confirmation_dialog_bar(
            game_presenter=game_presenter, htmx_attrs=htmx_attrs, board_id=board_id
        )

    inner_content = div(
        p(
            "Game against ",
            b(game_presenter.opponent_username),
            " on Lichess. ",
            f"Turn #{game_presenter.chess_board.fullmove_number}",
            cls="text-center",
        ),
        p(
            "Your turn! 🙂"
            if game_presenter.is_my_turn
            else "Waiting for them to move. ⏳",
            cls="text-center",
        ),
    )

    return companion_bar(
        inner_content,
        id_=f"chess-board-lichess-bridge-bar-{board_id}",
        position="top",
        htmx_attrs=htmx_attrs,
    )


def move_piece_confirmation_dialog_bar(
    *,
    game_presenter: LichessCorrespondenceGamePresenter,
    htmx_attrs: dict[str, str] | None = None,
    board_id: str,
) -> dom_tag:
    assert game_presenter.selected_piece is not None
    assert game_presenter.target_square_to_confirm is not None

    htmx_attrs_confirm = {
        "data_hx_post": "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_move_piece",
                    kwargs={
                        "game_id": game_presenter.game_id,
                        "from_": game_presenter.selected_piece.square,
                        "to": game_presenter.target_square_to_confirm,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }
    htmx_attrs_cancel = {
        "data_hx_get": "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_no_selection",
                    kwargs={"game_id": game_presenter.game_id},
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        ),
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_swap": "outerHTML",
    }

    return confirmation_dialog_bar(
        question=div(
            "Move this ",
            b(game_presenter.selected_piece.piece_name),
            " from ",
            b(game_presenter.selected_piece.square),
            " to ",
            b(game_presenter.target_square_to_confirm),
            "?",
            cls="text-center",
        ),
        htmx_attrs_confirm=htmx_attrs_confirm,
        htmx_attrs_cancel=htmx_attrs_cancel,
        id_=f"chess-board-lichess-bridge-bar-{board_id}",
        htmx_attrs=htmx_attrs,
    )

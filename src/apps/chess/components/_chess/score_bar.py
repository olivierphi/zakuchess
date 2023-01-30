from typing import TYPE_CHECKING

from dominate.dom_tag import dom_tag
from dominate.tags import div, img

from ...domain.helpers import piece_name_from_piece_type
from ..chess_helpers import chess_unit_symbol_url

if TYPE_CHECKING:
    from ...domain.types import PlayerSide
    from ...presenters import GamePresenter


def chess_score_bar(game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    score = game_presenter.score
    score_display = "Draw"
    if score != 0:
        i_am_leading = score > 0 and game_presenter.my_side == "w" or score < 0 and game_presenter.my_side == "b"
        score_display = "".join(("You're" if i_am_leading else "Opponent are", f" leading by {abs(score)} points"))
        if abs(score) > 5:
            score_display += " 🙂" if i_am_leading else " 🙁"

    captured_pieces_to_display: dict["PlayerSide", list[dom_tag]] = {"w": [], "b": []}
    for player_side, captured_pieces in game_presenter.captured_pieces.items():
        for captured_piece in captured_pieces:
            piece_name = piece_name_from_piece_type(captured_piece)
            captured_pieces_to_display[player_side].append(
                img(
                    src=chess_unit_symbol_url(player_side=player_side, piece_name=piece_name),
                    alt=piece_name,
                    cls="inline w-5 aspect-square",
                )
            )

    captures_display_left = captured_pieces_to_display["b"]
    captures_display_right = captured_pieces_to_display["w"]

    return div(
        div(captures_display_left),
        div(score_display),
        div(captures_display_right),
        cls="h-10 flex justify-evenly w-full text-slate-50 size-lg items-center bg-orange-800 border-2 border-solid border-slate-50",
    )

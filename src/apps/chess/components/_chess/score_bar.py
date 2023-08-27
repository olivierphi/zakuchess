from typing import TYPE_CHECKING

from dominate.dom_tag import dom_tag
from dominate.tags import div, span

from ...domain.helpers import piece_name_from_piece_type
from ..chess_helpers import chess_unit_symbol_class

if TYPE_CHECKING:
    from ...domain.types import PlayerSide
    from ...presenters import GamePresenter


def chess_score_bar(game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    from ..chess import INFO_BARS_COMMON_CLASSES

    score = game_presenter.score
    score_display = "Draw"
    if score != 0:
        i_am_leading = score > 0 and game_presenter.my_side == "w" or score < 0 and game_presenter.my_side == "b"
        score_display = "".join(("You're" if i_am_leading else "Opponent are", f" {abs(score)} points ahead"))
        if abs(score) > 5:
            score_display += " 🙂" if i_am_leading else " 🙁"

    captured_pieces_to_display: dict["PlayerSide", list[dom_tag]] = {"w": [], "b": []}
    for player_side, captured_pieces in game_presenter.captured_pieces.items():
        for captured_piece in captured_pieces:
            piece_name = piece_name_from_piece_type(captured_piece)
            captured_pieces_to_display[player_side].append(
                span(
                    cls=" ".join(
                        (
                            "inline-block",
                            "w-5",
                            "aspect-square",
                            "bg-no-repeat",
                            "bg-cover",
                            chess_unit_symbol_class(player_side=player_side, piece_name=piece_name),
                        )
                    )
                )
            )

    captures_display_left = captured_pieces_to_display["b"]
    captures_display_right = captured_pieces_to_display["w"]

    return div(
        div(captures_display_left, cls="min-w-[5rem]"),
        div(score_display),
        div(captures_display_right, cls="min-w-[5rem]"),
        cls=f"min-h-[2.5rem] flex justify-between w-full size-lg items-center {INFO_BARS_COMMON_CLASSES} border-t-0",
    )

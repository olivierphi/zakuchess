from typing import TYPE_CHECKING

import pytest

from ...business_logic import do_chess_move

if TYPE_CHECKING:
    from ...types import FEN, ChessMoveResult, Square


@pytest.mark.parametrize(
    (
        "starting_fen",
        "move",
        "expected_fen_after_en_passant",
        "expected_chess_move_result",
    ),
    (
        # @link https://lichess.org/editor/
        (
            # white to play:
            "7k/8/8/pP6/8/8/8/7K w - a6 0 1",
            ("b5", "a6"),
            "7k/8/P7/8/8/8/8/7K b - - 0 1",
            {
                "b5": "a6",  # the pawn's move itself
                "a5": None,  # the capture of the other pawn, via "en passant"
            },
        ),
        (
            # black to play:
            "7k/8/8/8/Pp6/8/8/7K b - a3 0 1",
            ("b4", "a3"),
            "7k/8/8/8/8/p7/8/7K w - - 0 2",
            {
                "b4": "a3",  # the pawn's move itself
                "a4": None,  # the capture of the other pawn, via "en passant"
            },
        ),
    ),
)
def test_can_manage_en_passant_correctly(
    starting_fen: "FEN",
    move: "tuple[Square, Square]",
    expected_fen_after_en_passant: "FEN",
    expected_chess_move_result: "ChessMoveResult",
):
    result: "ChessMoveResult" = do_chess_move(
        fen=starting_fen, from_=move[0], to=move[1]
    )

    assert result["is_capture"] is True
    assert result["fen"] == expected_fen_after_en_passant
    assert result["changes"] == expected_chess_move_result

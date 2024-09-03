import pytest

from apps.daily_challenge.management.commands.dailychallenge_create_from_lichess_puzzles_csv import (
    BotFirstMoveAndResultingFen,
    get_bot_first_move_and_resulting_fen,
)


@pytest.mark.parametrize(
    ("lichess_puzzle_fen", "lichess_puzzle_moves", "expected_result"),
    [
        (
            # Black to move: simple case
            "8/3b2kp/8/8/p1pp4/P7/K4R1b/2B5 b - - 1 39",
            "h2g3 f2g2 g7f6 g2g3",
            BotFirstMoveAndResultingFen(
                "h2g3", "8/3b2kp/8/8/p1pp4/P5b1/K4R2/2B5 w - - 2 40"
            ),
        ),
        (
            # White to move: the board will have to be mirrored, so *we*
            # start on the white side
            "r1r3k1/4qpbp/1B2p1p1/p2b4/8/PP2PN2/4QPPP/2R2RK1 w - - 1 21",
            "b6c5 c8c5 c1c5 e7c5",
            BotFirstMoveAndResultingFen(
                # First move was mirrored too ("b6c5" -> "b3c4")
                "b3c4",
                "2r2rk1/4qppp/pp2pn2/8/P1bB4/4P1P1/4QPBP/R1R3K1 w - - 2 22",
            ),
        ),
    ],
)
def test_get_bot_first_move_and_resulting_fen(
    lichess_puzzle_fen: str,
    lichess_puzzle_moves: str,
    expected_result: BotFirstMoveAndResultingFen,
):
    lichess_csv_row = {"FEN": lichess_puzzle_fen, "Moves": lichess_puzzle_moves}
    result = get_bot_first_move_and_resulting_fen(lichess_csv_row)
    assert result == expected_result

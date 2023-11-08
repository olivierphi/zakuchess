import pytest

from ..models import DailyChallenge, DailyChallengeStatus


@pytest.fixture
def challenge_minimalist() -> DailyChallenge:
    """
    Returns a DailyChallenge object that has the following board:

      a b c d e f g h
    8 k . . . . . . .
    7 p p . . . Q . .
    6 . . . . . . . p
    5 . . . . . . . .
    4 . . . . . . . .
    3 . . . . . . . .
    2 . . . . . . . B
    1 K . . . . . . .

    @link https://lichess.org/editor/k7/pp3Q2/7p/8/8/8/7B/K7_w_-_-_0_1?color=white
    """
    return DailyChallenge.objects.create(
        fen="k7/pp3Q2/7p/8/8/8/7B/K7 w - - 0 2",
        lookup_key="test-minimal",
        source="test",
        status=DailyChallengeStatus.PUBLISHED,
        bot_first_move="b8a8",
        intro_turn_speech_square="h2",
        # Inferred fields:
        starting_advantage=9000,
        intro_turn_speech_text="",
        piece_role_by_square={
            "a8": "k",
            "f7": "Q",
            "b7": "p1",
            "a7": "p2",
            "h6": "p3",
            "h2": "B1",
            "a1": "K",
        },
        teams={
            "w": [
                {"role": "Q", "name": ["QUEEN", "1"], "faction": "humans"},
                {"role": "B1", "name": ["BISHOP", "1"], "faction": "humans"},
                {"role": "K", "name": ["KING", "1"], "faction": "humans"},
            ],
            "b": [
                {"role": "k", "name": "", "faction": "undeads"},
                {"role": "p1", "name": "", "faction": "undeads"},
                {"role": "p2", "name": "", "faction": "undeads"},
                {"role": "p3", "name": "", "faction": "undeads"},
            ],
        },
        fen_before_bot_first_move="1k6/pp3Q2/7p/8/8/8/7B/K7 b - - 0 1",
        piece_role_by_square_before_bot_first_move={
            "f7": "Q",
            "b7": "p1",
            "a7": "p2",
            "h6": "p3",
            "h2": "B1",
            "a1": "K",
            "b8": "k",
        },
    )

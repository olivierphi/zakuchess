import pytest

from ..models import (
    DailyChallenge,
    DailyChallengeStatus,
    PlayerGameOverState,
    PlayerGameState,
)

_MINIMALIST_GAME = {
    "fen": "k7/pp3Q2/7p/8/8/8/7B/K7 w - - 0 2",
    "piece_role_by_square": {
        "a8": "k",
        "f7": "Q",
        "b7": "p1",
        "a7": "p2",
        "h6": "p3",
        "h2": "B1",
        "a1": "K",
    },
}


@pytest.fixture
def challenge_minimalist() -> DailyChallenge:
    """
    Returns a DailyChallenge object that has the following board:
    (winnable in 1 move)

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
        fen=_MINIMALIST_GAME["fen"],
        lookup_key="test-minimal",
        source="test",
        status=DailyChallengeStatus.PUBLISHED,
        bot_first_move="b8a8",
        intro_turn_speech_square="h2",
        # Inferred fields:
        starting_advantage=9_000,  # it could even be over this...
        intro_turn_speech_text="",
        solution="f7f8",
        solution_turns_count=1,
        piece_role_by_square=_MINIMALIST_GAME["piece_role_by_square"],
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


def challenge_quick(challenge_minimalist: DailyChallenge) -> DailyChallenge:
    """
    Same than `challenge_minimalist`, but with a few turns to reach victory.
    (winnable in 1 move)

      a b c d e f g h
    8 k . . . . . . .
    7 . p . . . Q . .
    6 p . . . . . . p
    5 . . . . . . . .
    4 . . . . . . . .
    3 . . . . . . . .
    2 . . . . . . . B
    1 K . . . . . . .
    """

    challenge_minimalist.fen = "k7/1p3Q2/p6p/8/8/8/7B/K7 w - - 0 1"
    challenge_minimalist.solution = "f7f8,a8a7,f8d6,a6a5,h2g1,b7b6,d6b6,a7a8,b6a7"
    challenge_minimalist.solution_turns_count = 5
    challenge_minimalist.fen_before_bot_first_move = "k7/pp3Q2/7p/8/8/8/7B/K7 b - - 0 1"
    challenge_minimalist.piece_role_by_square_before_bot_first_move = {
        "f7": "Q",
        "b7": "p1",
        "a7": "p2",
        "h6": "p3",
        "h2": "B1",
        "a1": "K",
        "a8": "k",
    }
    challenge_minimalist.save()
    return challenge_minimalist


@pytest.fixture
def player_game_state_minimalist() -> PlayerGameState:
    """Same data than challenge_minimalist, but in PlayerGameState format."""
    return PlayerGameState(
        attempts_counter=0,
        turns_counter=0,
        current_attempt_turns_counter=0,
        fen=_MINIMALIST_GAME["fen"],  # type: ignore
        piece_role_by_square=_MINIMALIST_GAME["piece_role_by_square"],  # type: ignore
        moves="",
        game_over=PlayerGameOverState.PLAYING,
    )

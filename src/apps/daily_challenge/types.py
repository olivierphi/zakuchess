from typing import NamedTuple, TypeAlias

import msgspec

from apps.chess.types import FEN, PieceRoleBySquare

GameID: TypeAlias = str


class PlayerGameState(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # Let's make the cookie content a bit shorter, with shorter field names
        "attempts_counter": "ac",
        "turns_counter": "tc",
        "current_attempt_turns_counter": "catc",
        "fen": "f",
        "piece_role_by_square": "prbs",
        "moves": "m",
    },
):
    """
    This is the state of a daily challenge, stored in a cookie for the player.
    """

    attempts_counter: int
    turns_counter: int
    current_attempt_turns_counter: int
    fen: FEN
    piece_role_by_square: PieceRoleBySquare
    # Each move is 4 more chars added there (UCI notation).
    # These are the moves *of the current attempt* only.
    moves: str


class PlayerSessionContent(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # Let's make the cookie content a bit shorter, with shorter field names
        "encoding_version": "ev",
        "games": "g",
    },
):
    """
    This is the whole content of the session cookie for the player.
    """

    encoding_version: int = 1
    games: dict[GameID, PlayerGameState]


class ChallengeTurnsState(NamedTuple):
    # the number of attempts the player has made for today's challenge:
    attempts_counter: int
    # The number of turns in the current attempt:
    current_attempt_turns: int
    turns_total: int
    turns_left: int
    percentage_left: int
    time_s_up: bool  # `True` when there are no more turns left for today's challenge.

import enum
from datetime import date
from typing import Literal, NamedTuple, TypeAlias

import msgspec

from apps.chess.types import FEN, PieceRoleBySquare

GameID: TypeAlias = str


@enum.unique
class PlayerGameOverState(enum.IntEnum):
    """
    This is the state of a daily challenge, stored in a cookie for the player.
    """

    # The player has not won yet, and has not lost yet.
    # They can still play.
    PLAYING = 0
    # The player has won the challenge.
    WON = 1
    # The player has lost the challenge.
    LOST = -1


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
        "game_over": "go",
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
    game_over: PlayerGameOverState = PlayerGameOverState.PLAYING


class PlayerStats(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # ditto
        "games_count": "gc",
        "win_count": "wc",
        "current_streak": "cs",
        "max_streak": "ms",
        "last_played": "lp",
        "wins_distribution": "wd",
    },
):
    """
    This is the stats of the player for daily challenges, stored in a cookie.
    """

    games_count: int = 0
    win_count: int = 0
    current_streak: int = 0
    max_streak: int = 0
    last_played: date | None = None
    wins_distribution: dict[Literal[1, 2, 3, 4, 5], int] = msgspec.field(
        default_factory=lambda: {
            1: 0,  # challenges won in less than a 5th of the turns allowance
            2: 0,  # challenges won in less than 2/5th of the turns allowance
            3: 0,  # ditto for 3/5th
            4: 0,  # ditto for 4/5th
            5: 0,  # won in the last few turns
        }
    )

    @property
    def win_rate(self) -> int:
        if self.games_count == 0 or self.win_count == 0:
            return 0
        return int(self.win_count / self.games_count * 100)


class PlayerSessionContent(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # ditto
        "encoding_version": "ev",
        "games": "g",
        "stats": "s",
    },
):
    """
    This is the whole content of the session cookie for the player.
    """

    encoding_version: int = 1
    games: dict[GameID, PlayerGameState]
    stats: PlayerStats | None  # TODO: remove the `| None` when we migrated all cookies


class ChallengeTurnsState(NamedTuple):
    # the number of attempts the player has made for today's challenge:
    attempts_counter: int
    # The number of turns in the current attempt:
    current_attempt_turns: int
    turns_total: int
    turns_left: int
    percentage_left: int
    time_s_up: bool  # `True` when there are no more turns left for today's challenge.

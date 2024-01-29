import enum
import math
from datetime import date
from typing import ClassVar, Literal, NamedTuple, Self, TypeAlias

import msgspec

from apps.chess.types import FEN, PieceRoleBySquare

GameID: TypeAlias = str


@enum.unique
class PlayerGameOverState(enum.IntEnum):
    """
    This is the state of a daily challenge,
    stored within a PlayerSessionContent (so, in a cookie).
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
    This is the state of a daily challenge,
    stored within a PlayerSessionContent (so, in a cookie).

    Counters are zero-based.
    """

    attempts_counter: int  # the number of attempts for today's challenge - 0-based
    turns_counter: int  # the sum of number of turns for all today's attempts
    current_attempt_turns_counter: int  # the number of turns for the current attempt
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
        "last_won": "lw",
        "wins_distribution": "wd",
    },
):
    """
    This is the stats of the player for daily challenges,
    stored within a PlayerSessionContent (so, in a cookie).
    """

    WINS_DISTRIBUTION_SLICE_COUNT: ClassVar[int] = 5

    games_count: int = 0
    win_count: int = 0
    current_streak: int = 0
    max_streak: int = 0
    last_played: date | None = None
    last_won: date | None = None
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
        """
        Because it's frustrating to see 99% when one lost only 1 game amongst many wins,
        this win rate is rounded up.
        """
        if self.games_count == 0 or self.win_count == 0:
            return 0
        return math.ceil(self.win_count / self.games_count * 100)


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
    stats: PlayerStats

    def to_cookie_content(self) -> str:
        return msgspec.json.encode(self).decode()

    @classmethod
    def from_cookie_content(cls, cookie_content: str) -> Self:
        return msgspec.json.decode(cookie_content.encode(), type=cls)


class ChallengeTurnsState(NamedTuple):
    # the number of attempts the player has made for today's challenge:
    attempts_counter: int
    # The number of turns in the current attempt:
    current_attempt_turns: int
    turns_total: int
    turns_left: int
    percentage_left: int
    time_s_up: bool  # `True` when there are no more turns left for today's challenge.

from typing import Literal, TypeAlias

import msgspec
from django.db import models

from apps.chess.types import FEN  # used by msgspec, so it has to be a "real" import

LichessAccessToken: TypeAlias = str  # e.g. "lio_6EeGimHMalSVH9qMcfUc2JJ3xdBPlqrL"

LichessPlayerId: TypeAlias = str  # e.g. "dunsap"
LichessPlayerFullId: TypeAlias = str  # e.g. "Dunsap"

LichessGameSeekId: TypeAlias = str  # e.g. "oIsGhJaf"

LichessGameId: TypeAlias = str  # e.g. "tFfGsEpb" (always 8 chars)
LichessGameFullId: TypeAlias = str  # e.g. "tFfGsEpbd0mL" (always 12 chars?)

# > By convention tokens have a recognizable prefix, but do not rely on this.
# Well... Let's still rely on this for now ^^
# TODO: remove this, as it may break one day?
LICHESS_ACCESS_TOKEN_PREFIX = "lio_"

# The values of these enums can be found in the OpenAPI spec one can download
# by clicking the "Download" button at the top of this page:
# https://lichess.org/api
# (for some reason the JSON file is not directly linkable)
LichessChessVariant = Literal[
    # we only support "standard" for now 😅
    # But as python-chess supports many variants, we could support more in the future.
    # (https://python-chess.readthedocs.io/en/latest/variant.html)
    "standard",
    "chess960",
    "crazyhouse",
    "antichess",
    "atomic",
    "horde",
    "kingOfTheHill",
    "racingKings",
    "threeCheck",
    "fromPosition",
]
LichessPlayerSide = Literal["white", "black"]
LichessGameSource = Literal["lobby", "friend"]  # TODO: other values?
LichessGameSpeed = Literal[
    "ultraBullet", "bullet", "blitz", "rapid", "classical", "correspondence"
]
LichessGamePerf = Literal[
    "ultraBullet",
    "bullet",
    "blitz",
    "rapid",
    "classical",
    "correspondence",
    "chess960",
    "crazyhouse",
    "antichess",
    "atomic",
    "horde",
    "kingOfTheHill",
    "racingKings",
    "threeCheck",
]
LichessGameStatus = Literal[
    "created",
    "started",
    "aborted",
    "mate",
    "resign",
    "stalemate",
    "timeout",
    "draw",
    "outoftime",
    "cheat",
    "noStart",
    "unknownFinish",
    "variantEnd",
]


class LichessCorrespondenceGameDaysChoice(models.IntegerChoices):
    # https://lichess.org/api#tag/Board/operation/apiBoardSeek
    ONE_DAY = (1, "1 days")
    TWO_DAYS = (2, "2 days")
    THREE_DAYS = (3, "3 days")
    FIVE_DAYS = (5, "5 days")
    SEVEN_DAYS = (7, "7 days")
    TEN_DAYS = (10, "10 days")
    FOURTEEN_DAYS = (14, "14 days")


class LichessAccountInformation(
    msgspec.Struct,
):
    """Information about an account, as returned by the Lichess API."""

    # N.B. There are many more fields than this - but we only use these at the moment

    id: LichessPlayerId
    username: LichessPlayerFullId
    url: str  # e.g. "https://lichess.org/@/dunsap"


class LichessOpponentData(msgspec.Struct):
    """Information about an opponent, as returned by the Lichess API."""

    id: LichessPlayerId
    username: LichessPlayerFullId
    rating: int  # e.g. 1790


class LichessOngoingGameData(msgspec.Struct):
    """Information about an ongoing game, as returned by the Lichess API."""

    gameId: LichessGameId
    fullId: LichessGameFullId
    color: LichessPlayerSide
    fen: FEN
    hasMoved: bool
    isMyTurn: bool
    lastMove: str  # e.g. "b8c6"
    opponent: LichessOpponentData
    perf: LichessGamePerf
    rated: bool
    secondsLeft: int
    source: LichessGameSource
    speed: LichessGameSpeed
    variant: dict[str, str]


class LichessGameUser(msgspec.Struct):
    id: LichessPlayerId
    name: LichessGameFullId


class LichessGameOpening(msgspec.Struct):
    eco: str  # e.g. "B01"
    name: str  # e.g. "Scandinavian Defense"
    ply: int  # e.g. 2


class LichessGamePlayer(msgspec.Struct):
    user: LichessGameUser
    rating: int
    provisional: bool = False


class LichessGamePlayers(msgspec.Struct):
    white: LichessGamePlayer
    black: LichessGamePlayer


class LichessGameExport(msgspec.Struct):
    """
    Information about a game as given by an "export game" endpoint,
    as returned by the Lichess API.
    """

    id: LichessGameId
    fullId: LichessGameFullId
    rated: bool
    variant: str
    speed: LichessGameSpeed
    perf: LichessGamePerf
    createdAt: int
    lastMoveAt: int
    status: LichessGameStatus
    source: LichessGameSource
    players: LichessGamePlayers
    opening: LichessGameOpening
    moves: str
    pgn: str
    daysPerTurn: int
    division: dict  # ???

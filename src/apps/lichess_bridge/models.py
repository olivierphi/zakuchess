import dataclasses
import functools
import io
from typing import TYPE_CHECKING, Literal, NamedTuple, TypeAlias

import chess.pgn
import msgspec
from django.db import models

from apps.chess.types import FEN  # used by msgspec, so it has to be a "real" import

if TYPE_CHECKING:
    import chess

    from apps.chess.types import PlayerSide

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


# Presenters are the objects we pass to our templates.
_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING: dict["LichessPlayerSide", "PlayerSide"] = {
    "white": "w",
    "black": "b",
}


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


class LichessGameExportMetadataPlayer(NamedTuple):
    id: LichessPlayerId
    username: LichessGameFullId
    player_side: "PlayerSide"


class LichessGameExportMetadataPlayers(NamedTuple):
    """
    Information about the players of a game, structured in a "me" and "them" way, and
    giving us the "active player" as well.

    (as opposed to the "players" field in the LichessGameExport class, which tells us
    who the "white" and "black" players are but without telling us which one is "me",
    or which one is the current active player)
    """

    me: LichessGameExportMetadataPlayer
    them: LichessGameExportMetadataPlayer
    active_player: Literal["me", "them"]


@dataclasses.dataclass
class LichessGameExportWithMetadata:
    """
    Wraps a LichessGameExport object with some additional metadata related to the
    current player.
    """

    game_export: LichessGameExport
    my_player_id: "LichessPlayerId"

    @functools.cached_property
    def chess_board(self) -> "chess.Board":
        pgn_game = chess.pgn.read_game(io.StringIO(self.game_export.pgn))
        if not pgn_game:
            raise ValueError("Could not read PGN game")
        return pgn_game.end().board()

    @functools.cached_property
    def active_player_side(self) -> "LichessPlayerSide":
        return "white" if self.chess_board.turn else "black"

    @functools.cached_property
    def players_from_my_perspective(self) -> "LichessGameExportMetadataPlayers":
        my_side: "LichessPlayerSide" = (
            "white"
            if self.game_export.players.white.user.id == self.my_player_id
            else "black"
        )
        their_side: "LichessPlayerSide" = "black" if my_side == "white" else "white"

        my_player: "LichessGameUser" = getattr(self.game_export.players, my_side).user
        their_player: "LichessGameUser" = getattr(
            self.game_export.players, their_side
        ).user

        result = LichessGameExportMetadataPlayers(
            me=LichessGameExportMetadataPlayer(
                id=my_player.id,
                username=my_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[my_side],
            ),
            them=LichessGameExportMetadataPlayer(
                id=their_player.id,
                username=their_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[their_side],
            ),
            active_player="me" if self.active_player_side == my_side else "them",
        )

        return result

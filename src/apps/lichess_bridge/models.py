import dataclasses
import functools
import io
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal, NamedTuple, TypeAlias

import chess.pgn
import msgspec
from django.db import models

from apps.chess.models import GameFactions
from apps.chess.types import FEN

from .business_logic import rebuild_game_from_moves, rebuild_game_from_pgn

if TYPE_CHECKING:
    from collections.abc import Sequence

    import chess

    from apps.chess.models import GameTeams
    from apps.chess.types import (
        BoardOrientation,
        Faction,
        PieceRoleBySquare,
        PlayerSide,
        UCIMove,
    )

    from .business_logic import RebuildGameFromMovesResult, RebuildGameFromPgnResult

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

# For now we hard-code the fact that "me" always plays the "humans" faction,
# and "them" always plays the "undeads" faction.
_FACTIONS_BY_BOARD_ORIENTATION: dict["BoardOrientation", GameFactions] = {
    "1->8": GameFactions(w="humans", b="undeads"),
    "8->1": GameFactions(w="undeads", b="humans"),
}

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


class LichessVariantStruct(msgspec.Struct):
    key: str  # e.g. "standard"
    name: str  # e.g. "Standard"
    short: str  # e.g. "Std"


class LichessPerfStruct(msgspec.Struct):
    name: str  # Translated perf name (e.g. "Correspondence", "Classical" or "Blitz")


class LichessGameEventPlayer(msgspec.Struct):
    id: LichessPlayerId
    name: LichessGameFullId
    rating: int
    title: str | None = None  # ??
    provisional: bool | None = None


class LichessGameState(msgspec.Struct):
    type: str  # e.g. "gameState"
    moves: str  # e.g. "e2e4 d7d5 f2f3 e7e5 f1d3 f8c5 b2b3"
    wtime: int  # e.g. 259200000
    btime: int  # e.g. 255151000
    winc: int  # e.g. 0
    binc: int  # e.g. 0
    status: LichessGameStatus


class LichessGameFullFromStream(msgspec.Struct):
    id: str
    variant: LichessVariantStruct
    speed: str
    perf: LichessPerfStruct
    rated: bool
    createdAt: int
    white: LichessGameEventPlayer
    black: LichessGameEventPlayer
    initialFen: FEN | Literal["startpos"]
    daysPerTurn: int
    type: Literal["gameFull"]
    state: LichessGameState

    @property
    def is_ongoing_game(self) -> bool:
        return self.state.status == "started"


class LichessGameWithMetadataBase(ABC):
    @property
    @abstractmethod
    def chess_board(self) -> "chess.Board": ...

    @property
    @abstractmethod
    def moves(self) -> "Sequence[UCIMove]": ...

    @property
    @abstractmethod
    def piece_role_by_square(self) -> "PieceRoleBySquare": ...

    @property
    @abstractmethod
    def teams(self) -> "GameTeams": ...

    @functools.cached_property
    def active_player_side(self) -> "LichessPlayerSide":
        return "white" if self.chess_board.turn else "black"

    @property
    @abstractmethod
    def players_from_my_perspective(self) -> "LichessGameMetadataPlayers": ...

    @functools.cached_property
    def board_orientation(self) -> "BoardOrientation":
        return self._players_sides.board_orientation

    @functools.cached_property
    def game_factions(self) -> GameFactions:
        return _FACTIONS_BY_BOARD_ORIENTATION[self.board_orientation]

    @property
    @abstractmethod
    def _players_sides(self) -> "LichessGameMetadataPlayerSides": ...


@dataclasses.dataclass(frozen=True)
class LichessGameFullFromStreamWithMetadata(LichessGameWithMetadataBase):
    """
    Wraps a LichessGameFullFromStream object with some additional metadata related to the
    current player, and some cached properties describing the state of the game.
    """

    raw_data: LichessGameFullFromStream
    my_player_id: "LichessPlayerId"

    @functools.cached_property
    def chess_board(self) -> "chess.Board":
        return self._rebuilt_game.chess_board

    @functools.cached_property
    def moves(self) -> "Sequence[UCIMove]":
        return self._rebuilt_game.moves

    @functools.cached_property
    def piece_role_by_square(self) -> "PieceRoleBySquare":
        return self._rebuilt_game.piece_role_by_square

    @functools.cached_property
    def teams(self) -> "GameTeams":
        return self._rebuilt_game.teams

    @functools.cached_property
    def active_player_side(self) -> "LichessPlayerSide":
        return "white" if self.chess_board.turn else "black"

    @functools.cached_property
    def players_from_my_perspective(self) -> "LichessGameMetadataPlayers":
        my_side, their_side, _ = self._players_sides

        my_player: "LichessGameEventPlayer" = getattr(self.raw_data, my_side)
        their_player: "LichessGameEventPlayer" = getattr(self.raw_data, their_side)

        result = LichessGameMetadataPlayers(
            me=LichessGameMetadataPlayer(
                id=my_player.id,
                username=my_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[my_side],
                faction="humans",
            ),
            them=LichessGameMetadataPlayer(
                id=their_player.id,
                username=their_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[their_side],
                faction="undeads",
            ),
            active_player="me" if self.active_player_side == my_side else "them",
        )

        return result

    @functools.cached_property
    def _players_sides(self) -> "LichessGameMetadataPlayerSides":
        my_side: "LichessPlayerSide" = (
            "white" if self.raw_data.white.id == self.my_player_id else "black"
        )
        their_side: "LichessPlayerSide" = "black" if my_side == "white" else "white"
        board_orientation: "BoardOrientation" = "1->8" if my_side == "white" else "8->1"

        return LichessGameMetadataPlayerSides(
            me=my_side,
            them=their_side,
            board_orientation=board_orientation,
        )

    @functools.cached_property
    def _rebuilt_game(self) -> "RebuildGameFromMovesResult":
        return rebuild_game_from_moves(
            uci_moves=self.raw_data.state.moves.strip().split(" "),
            factions=self.game_factions,
        )


@dataclasses.dataclass(frozen=True)
class LichessGameExportWithMetadata(LichessGameWithMetadataBase):
    """
    Wraps a LichessGameExport object with some additional metadata related to the
    current player, and some cached properties describing the state of the game.
    """

    raw_data: LichessGameExport
    my_player_id: "LichessPlayerId"

    @functools.cached_property
    def pgn_game(self) -> "chess.pgn.Game":
        pgn_game = chess.pgn.read_game(io.StringIO(self.raw_data.pgn))
        if not pgn_game:
            raise ValueError("Could not read PGN game")
        return pgn_game

    @functools.cached_property
    def chess_board(self) -> "chess.Board":
        return self._rebuilt_game.chess_board

    @functools.cached_property
    def moves(self) -> "Sequence[UCIMove]":
        return self._rebuilt_game.moves

    @functools.cached_property
    def piece_role_by_square(self) -> "PieceRoleBySquare":
        return self._rebuilt_game.piece_role_by_square

    @functools.cached_property
    def teams(self) -> "GameTeams":
        return self._rebuilt_game.teams

    @functools.cached_property
    def active_player_side(self) -> "LichessPlayerSide":
        return "white" if self.chess_board.turn else "black"

    @functools.cached_property
    def players_from_my_perspective(self) -> "LichessGameMetadataPlayers":
        my_side, their_side, _ = self._players_sides

        my_player: "LichessGameUser" = getattr(self.raw_data.players, my_side).user
        their_player: "LichessGameUser" = getattr(
            self.raw_data.players, their_side
        ).user

        result = LichessGameMetadataPlayers(
            me=LichessGameMetadataPlayer(
                id=my_player.id,
                username=my_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[my_side],
                faction="humans",
            ),
            them=LichessGameMetadataPlayer(
                id=their_player.id,
                username=their_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[their_side],
                faction="undeads",
            ),
            active_player="me" if self.active_player_side == my_side else "them",
        )

        return result

    @functools.cached_property
    def _players_sides(self) -> "LichessGameMetadataPlayerSides":
        my_side: "LichessPlayerSide" = (
            "white"
            if self.raw_data.players.white.user.id == self.my_player_id
            else "black"
        )
        their_side: "LichessPlayerSide" = "black" if my_side == "white" else "white"
        board_orientation: "BoardOrientation" = "1->8" if my_side == "white" else "8->1"

        return LichessGameMetadataPlayerSides(
            me=my_side,
            them=their_side,
            board_orientation=board_orientation,
        )

    @functools.cached_property
    def _rebuilt_game(self) -> "RebuildGameFromPgnResult":
        return rebuild_game_from_pgn(
            pgn_game=self.pgn_game, factions=self.game_factions
        )


class LichessGameMetadataPlayerSides(NamedTuple):
    me: "LichessPlayerSide"
    them: "LichessPlayerSide"
    board_orientation: "BoardOrientation"


class LichessGameMetadataPlayer(NamedTuple):
    id: LichessPlayerId
    username: LichessGameFullId
    player_side: "PlayerSide"
    faction: "Faction"


class LichessGameMetadataPlayers(NamedTuple):
    """
    Information about the players of a game, structured in a "me" and "them" way, and
    giving us the "active player" as well.

    (as opposed to the "players" field in the LichessGameExport class, which tells us
    who the "white" and "black" players are but without telling us which one is "me",
    or which one is the current active player)
    """

    me: LichessGameMetadataPlayer
    them: LichessGameMetadataPlayer
    active_player: Literal["me", "them"]

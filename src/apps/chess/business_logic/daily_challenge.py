from typing import TYPE_CHECKING, Final, TypeAlias, TypedDict

from .types import FEN

if TYPE_CHECKING:
    from .types import Factions, PieceRoleBySquare, PlayerSide

GameID: TypeAlias = str

MAXIMUM_TURNS_PER_CHALLENGE: "Final[int]" = 30

PLAYER_SIDE: "Final[PlayerSide]" = "w"
BOT_SIDE: "Final[PlayerSide]" = "b"
FACTIONS: "Final[Factions]" = {"w": "humans", "b": "undeads"}  # hard-coded for now


class PlayerGameState(TypedDict):
    turns_counter: int
    fen: "FEN"
    piece_role_by_square: "PieceRoleBySquare"


class PlayerSessionContent(TypedDict):
    games: dict[GameID, PlayerGameState]

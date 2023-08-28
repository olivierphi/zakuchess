from typing import TYPE_CHECKING, TypeAlias, TypedDict

from .types import FEN

if TYPE_CHECKING:
    from .types import PieceRoleBySquare

GameID: TypeAlias = str


class PlayerGameState(TypedDict):
    fen: "FEN"
    piece_role_by_square: "PieceRoleBySquare"


class PlayerSessionContent(TypedDict):
    games: dict[GameID, PlayerGameState]

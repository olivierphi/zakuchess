from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias, TypedDict

from .types import FEN

if TYPE_CHECKING:
    from .types import Factions, PieceRoleBySquare, PlayerSide

GameID: TypeAlias = str

MAXIMUM_TURNS_PER_CHALLENGE: "Final[int]" = 30

PLAYER_SIDE: "Final[PlayerSide]" = "w"
BOT_SIDE: "Final[PlayerSide]" = "b"
FACTIONS: "Final[Factions]" = {"w": "humans", "b": "undeads"}  # hard-coded for now


class PlayerSessionContent(TypedDict):
    # That is the content of the session cookie for the player.
    # Since it's just a Python dict, Django knows how to serialize it.
    games: dict[GameID, "PlayerGameState"]


class PlayerGameState(TypedDict):
    # That is the state of a daily challenge, stored in a cookie for the player.
    # Since it's just a Python dict, Django knows how to serialize it.
    attempts_counter: int
    turns_counter: int
    fen: "FEN"
    piece_role_by_square: "PieceRoleBySquare"


class ChallengeTurnsState(NamedTuple):
    attempts_counter: int
    turns_total: int
    turns_left: int
    percentage_left: int
    game_over: bool  # `True` when there are no more turns left for today's challenge.

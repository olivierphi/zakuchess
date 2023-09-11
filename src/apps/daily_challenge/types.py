from typing import TYPE_CHECKING, NamedTuple, TypeAlias, TypedDict

if TYPE_CHECKING:
    from apps.chess.types import FEN, PieceRoleBySquare

GameID: TypeAlias = str


class PlayerSessionContent(TypedDict):
    # That is the content of the session cookie for the player.
    # Since it's just a Python dict, Django knows how to serialize it.
    games: dict[GameID, "PlayerGameState"]


class PlayerGameState(TypedDict):
    # That is the state of a daily challenge, stored in a cookie for the player.
    # Since it's just a Python dict, Django knows how to serialize it.
    attempts_counter: int
    turns_counter: int
    current_attempt_turns_counter: int
    fen: "FEN"
    piece_role_by_square: "PieceRoleBySquare"


class ChallengeTurnsState(NamedTuple):
    # the number of attempts the player has made for today's challenge:
    attempts_counter: int
    # The number of turns in the current attempt:
    current_attempt_turns: int
    turns_total: int
    turns_left: int
    percentage_left: int
    time_s_up: bool  # `True` when there are no more turns left for today's challenge.

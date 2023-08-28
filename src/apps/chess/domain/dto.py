from typing import TYPE_CHECKING, Required, TypeAlias, TypedDict

if TYPE_CHECKING:
    from .types import FEN, ChessMoveChanges, Faction, GameEndReason, PieceType, PlayerSide, TeamMemberRole

# N.B. We use TypedDicts over NameTuples or Dataclasses here,
# as we want to be able to serialise these data structures in JSON :-)


class GameOverDescription(TypedDict):
    winner: "PlayerSide | None"
    reason: "GameEndReason"


class ChessMoveResult(TypedDict):
    fen: "FEN"
    changes: "ChessMoveChanges"
    is_capture: bool
    is_castling: bool
    promotion: "PieceType | None"
    game_over: GameOverDescription | None


class TeamMember(TypedDict, total=False):
    role: Required["TeamMemberRole"]
    first_name: str
    last_name: str
    faction: "Faction"


GameTeams: TypeAlias = dict["PlayerSide", list["TeamMember"]]

from typing import TYPE_CHECKING, TypedDict

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


class TeamMember(TypedDict):
    first_name: str
    last_name: str
    role: "TeamMemberRole"
    faction: "Faction"


class GameTeams(TypedDict):
    w: list[TeamMember]
    b: list[TeamMember]

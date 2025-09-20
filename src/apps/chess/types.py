from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NamedTuple, NotRequired, TypeAlias, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

# ---
# Description of a chess board:

File = Literal["a", "b", "c", "d", "e", "f", "g", "h"]
Rank = Literal["1", "2", "3", "4", "5", "6", "7", "8"]

# fmt: off
Square = Literal[
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
]
# fmt: on

BoardOrientation = Literal[
    "1-to-8",  # "w" player starting on the left-hand side
    "8-to-1",  # "b" player starting on the left-hand side
]

# ---
# Description of a chess game:

# https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
FEN: TypeAlias = str
# https://en.wikipedia.org/wiki/Portable_Game_Notation
PGN: TypeAlias = str

# fmt: off
PlayerSide = Literal[
    # Following chess conventions, our sides will be "w(hite)" and "b(lack)".
    "w",
    "b",
]
# fmt: on

# fmt: off
PieceType = Literal[
    # pawn, knight, bishop, rook, queen, king
    "p", "n", "b", "r", "q", "k",
]
# fmt: on

PieceName = Literal["pawn", "knight", "bishop", "rook", "queen", "king"]

Move: TypeAlias = tuple[Square, Square]  # from, to - e.g. `("e2", "e4")`
MoveUCI: TypeAlias = str  # e.g. `"e2e4"`

# ---
# Description of our own mechanisms, on top of the classic chess ones:
# This mostly consists in playing with "characters". We have to track their position
# as they move - e.g. the queen named "Ada Lovelace" should still have this name after a move.

CharacterId: TypeAlias = str
CharacterIdBySquare: TypeAlias = dict[Square, CharacterId]

GameTeamsDict: TypeAlias = "dict[PlayerSide, list[Character]]"


class Character(TypedDict):
    id: CharacterId
    type: PieceType
    name: NotRequired[Sequence[str]]
    promotion: NotRequired[PieceType]

    # We may have multiple factions in a single team later on, but this is not
    # implemented at the moment.
    # faction: Faction


Faction = Literal[
    "humans",
    "undead",
    # hopefully we'll add others later on :-)
]


class GameFactions(NamedTuple):
    w: Faction  # the faction for the "w" player
    b: Faction  # the faction for the "b" player

    def get_faction_for_side(self, item: PlayerSide) -> Faction:
        return getattr(self, item)

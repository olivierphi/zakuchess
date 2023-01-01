from typing import Literal, TypeAlias, TypedDict

PlayerSide = Literal[
    # Following chess conventions, our sides will be "w(hite)" and "b(lack)".
    # fmt: off
    "w",
    "b",
    # fmt: on
]

PieceSymbol = Literal[
    # fmt: off
    "P", "N", "B", "R", "Q", "K", # "w" side
    "p", "n", "b", "r", "q", "k",
    # "b" side
    # fmt: on
]

PieceRole = Literal[
    # fmt: off
    "p", "n", "b", "r", "q", "k",
    # fmt: on
]

TeamMemberRole = Literal[
    # fmt: off
    # 8 pawns:
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", 
    # 8 pieces:
    # N.B. Bishops are "b(lack)" or "w(hite)" rather than 1 or 2
    "r1", "n1", "bb", "q", "k", "bw", "n2", "r2",
    # fmt: on
]

File = Literal["a", "b", "c", "d", "e", "f", "g", "h"]
Rank = Literal["1", "2", "3", "4", "5", "6", "7", "8"]

Square = Literal[
    # fmt: off
    # N.B. copy-paste from chess.js :-)
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"
    # fmt: on
]

PieceId: TypeAlias = TeamMemberRole

PiecesIdPerSquare: TypeAlias = dict[Square, PieceId]


class PieceView(TypedDict):
    id: PieceId
    piece: PieceSymbol


PiecesView: TypeAlias = dict[Square, PieceView]
PieceIdsPerSquare: TypeAlias = dict[Square, PieceId]

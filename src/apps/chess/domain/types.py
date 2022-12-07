import dataclasses
from functools import cached_property
from typing import Literal, TypeAlias, TypedDict

PlayerSide = Literal[
    # Following chess conventions, our side will be "w(hite)" and "b(lack)".
    # fmt: off
    "w",
    "b",
    # fmt: on
]

PieceSymbol = Literal[
    # fmt: off
    "p", "n", "b", "r", "q", "k",
    "P", "N", "B", "R", "Q", "K",
    # fmt: on
]

Square = Literal[
    # fmt: off
    # N.B. copy-paste from chess.js :-)
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8" ,
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7" ,
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6" ,
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5" ,
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4" ,
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3" ,
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2" ,
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"
    # fmt: on
]

PieceId: TypeAlias = str

PiecesIdPerSquare: TypeAlias = dict[Square, PieceId]


class PieceView(TypedDict):
    id: PieceId
    piece: PieceSymbol


@dataclasses.dataclass(frozen=True)
class ChessBoardState:
    fen: str
    active_player: PlayerSide
    pieces_view: "PiecesView"
    selected_piece_square: Square | None = None

    def replace(self, **kwargs) -> "ChessBoardState":
        return dataclasses.replace(self, **kwargs)

    @cached_property
    def pieces_id_per_square(self) -> dict[Square, PieceId]:
        return {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}


PiecesView: TypeAlias = dict[Square, PieceView]
PieceIdsPerSquare: TypeAlias = dict[Square, PieceId]

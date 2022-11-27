from __future__ import annotations

from typing import Literal, TypeAlias, TypedDict

PlayerCode: TypeAlias = Literal["w", "b"]
PieceSymbol: TypeAlias = str
SquareName: TypeAlias = str

PieceId: TypeAlias = str

PIECES_VALUES: dict[PieceSymbol, int] = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
}


class PieceView(TypedDict):
    id: PieceId
    piece: PieceSymbol


PiecesView: TypeAlias = dict[SquareName, PieceView]
PieceIdsPerSquare: TypeAlias = dict[SquareName, PieceId]

from __future__ import annotations
from typing import TypeAlias, TypedDict, Literal

PlayerCode: TypeAlias = Literal["w", "b"]
PieceSymbol: TypeAlias = str
SquareName: TypeAlias = str

PieceId: TypeAlias = str


class PieceView(TypedDict):
    id: PieceId
    piece: PieceSymbol


PiecesView: TypeAlias = dict[SquareName, PieceView]
PieceIdsPerSquare: TypeAlias = dict[SquareName, PieceId]

from __future__ import annotations

import dataclasses
from typing import Literal, TypeAlias, TypedDict

PlayerSide = Literal["w", "b"]
PieceSymbol: TypeAlias = str
SquareName: TypeAlias = str

PieceId: TypeAlias = str

PiecesIdPerSquare: TypeAlias = dict[SquareName, PieceId]


class PieceView(TypedDict):
    id: PieceId
    piece: PieceSymbol


@dataclasses.dataclass
class ChessBoardState:
    fen: str
    active_player: PlayerSide
    pieces_view: PiecesView
    selected_piece_square: SquareName | None = None


PiecesView: TypeAlias = dict[SquareName, PieceView]
PieceIdsPerSquare: TypeAlias = dict[SquareName, PieceId]

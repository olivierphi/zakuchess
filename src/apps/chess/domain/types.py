import enum
from functools import cached_property
import dataclasses
from typing import TypeAlias, TypedDict


@enum.unique
class PlayerSide(str, enum.Enum):
    # Following chess conventions, our side will be "W(hite)" and "B(lack)".
    W = "w"
    B = "B"


PieceSymbol: TypeAlias = str
SquareName: TypeAlias = str

PieceId: TypeAlias = str

PiecesIdPerSquare: TypeAlias = dict[SquareName, PieceId]


class PieceView(TypedDict):
    id: PieceId
    piece: PieceSymbol


@dataclasses.dataclass(frozen=True)
class ChessBoardState:
    fen: str
    active_player: PlayerSide
    pieces_view: "PiecesView"
    selected_piece_square: SquareName | None = None

    def replace(self, **kwargs) -> "ChessBoardState":
        return dataclasses.replace(self, **kwargs)

    @cached_property
    def pieces_id_per_square(self) -> dict[SquareName, PieceId]:
        return {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}


PiecesView: TypeAlias = dict[SquareName, PieceView]
PieceIdsPerSquare: TypeAlias = dict[SquareName, PieceId]

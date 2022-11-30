from typing import Final
from .types import PieceSymbol

PIECES_VALUES: Final[dict[PieceSymbol, int]] = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
}

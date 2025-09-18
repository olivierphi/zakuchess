from typing import TypeAlias, Literal, Final

# Description of a chess board:

File = Literal["a", "b", "c", "d", "e", "f", "g", "h"]
Rank = Literal["1", "2", "3", "4", "5", "6", "7", "8"]

FILES: Final[tuple[File, ...]] = ("a", "b", "c", "d", "e", "f", "g", "h")
RANKS: Final[tuple[Rank, ...]] = ("1", "2", "3", "4", "5", "6", "7", "8")

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

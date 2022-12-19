from typing import Final

from .types import PieceRole, PieceSymbol, PlayerSide, Square

PLAYER_SIDES: Final[tuple[PlayerSide, PlayerSide]] = ("w", "b")

PIECES_VALUES: Final[dict[PieceSymbol, int]] = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
}

PIECES_ROLE_BY_STARTING_SQUARE: Final[dict[Square, PieceRole]] = {
    # Side "w":
    "a1": "r1",
    "b1": "n1",
    "c1": "bb",
    "d1": "q",
    "e1": "k",
    "f1": "bw",
    "g1": "n2",
    "h1": "r2",
    "a2": "p1",
    "b2": "p2",
    "c2": "p3",
    "d2": "p4",
    "e2": "p5",
    "f2": "p6",
    "g2": "p7",
    "h2": "p8",
    # Side "b":
    "a8": "r1",
    "b8": "n1",
    "c8": "bw",
    "d8": "q",
    "e8": "k",
    "f8": "bb",
    "g8": "n2",
    "h8": "r2",
    "a7": "p1",
    "b7": "p2",
    "c7": "p3",
    "d7": "p4",
    "e7": "p5",
    "f7": "p6",
    "g7": "p7",
    "h7": "p8",
}

STARTING_PIECES: dict[PlayerSide, tuple[PieceSymbol]] = {
    "w": (*("P" * 8), *("N" * 2), *("B" * 2), *("R" * 2), "Q", "K"),
    "b": (*("p" * 8), *("n" * 2), *("b" * 2), *("r" * 2), "q", "k"),
}

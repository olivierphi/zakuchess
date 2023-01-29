from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .types import PieceName, PieceRole, PieceSymbol, PieceType, PlayerSide, Square

PLAYER_SIDES: Final[tuple["PlayerSide", "PlayerSide"]] = ("w", "b")

PIECES_VALUES: Final[dict["PieceType", int]] = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
}

PIECES_ROLE_BY_STARTING_SQUARE: Final[dict["Square", "PieceRole"]] = {
    # Side "w":
    "a1": "R1",
    "b1": "N1",
    "c1": "BB",
    "d1": "Q",
    "e1": "K",
    "f1": "BW",
    "g1": "N2",
    "h1": "R2",
    "a2": "P1",
    "b2": "P2",
    "c2": "P3",
    "d2": "P4",
    "e2": "P5",
    "f2": "P6",
    "g2": "P7",
    "h2": "P8",
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

STARTING_PIECES: dict["PlayerSide", tuple["PieceSymbol"]] = {
    "w": (*("P" * 8), *("N" * 2), *("B" * 2), *("R" * 2), "Q", "K"),  # type: ignore
    "b": (*("p" * 8), *("n" * 2), *("b" * 2), *("r" * 2), "q", "k"),  # type: ignore
}

PIECE_TYPE_TO_NAME: dict["PieceType", "PieceName"] = {
    "p": "pawn",
    "n": "knight",
    "b": "bishop",
    "r": "rook",
    "q": "queen",
    "k": "king",
}

PIECE_TYPE_TO_UNICODE: dict["PieceType", str] = {
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}

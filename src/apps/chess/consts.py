from typing import TYPE_CHECKING, Final

import chess

if TYPE_CHECKING:
    from apps.chess.types import PieceName, PieceSymbol, PieceType, PlayerSide, Square

PLAYER_SIDES: Final[tuple["PlayerSide", "PlayerSide"]] = ("w", "b")

PIECES_VALUES: Final[dict["PieceType", int]] = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
}

SQUARES: Final[tuple["Square", ...]] = (
    # The order matters here, as we use that for the board visual representation.
    # fmt: off
    "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
    "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
    "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8",
    "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8",
    # fmt: on
)

STARTING_PIECES: dict["PlayerSide", tuple["PieceSymbol"]] = {
    "w": (*("P" * 8), *("N" * 2), *("B" * 2), *("R" * 2), "Q", "K"),  # type: ignore
    "b": (*("p" * 8), *("n" * 2), *("b" * 2), *("r" * 2), "q", "k"),  # type: ignore
}

PIECE_INT_TO_PIECE_TYPE: dict[int, "PieceType"] = {
    chess.PAWN: "p",
    chess.KNIGHT: "n",
    chess.BISHOP: "b",
    chess.ROOK: "r",
    chess.QUEEN: "q",
    chess.KING: "k",
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

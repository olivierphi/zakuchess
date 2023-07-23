from typing import TYPE_CHECKING, Final

import chess

if TYPE_CHECKING:
    from .types import PieceName, PieceSymbol, PieceType, PlayerSide, Square

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
    # "h8", "g8", "f8", "e8", "d8", "c8", "b8", "a8",
    # "h7", "g7", "f7", "e7", "d7", "c7", "b7", "a7",
    # "h6", "g6", "f6", "e6", "d6", "c6", "b6", "a6",
    # "h5", "g5", "f5", "e5", "d5", "c5", "b5", "a5",
    # "h4", "g4", "f4", "e4", "d4", "c4", "b4", "a4",
    # "h3", "g3", "f3", "e3", "d3", "c3", "b3", "a3",
    # "h2", "g2", "f2", "e2", "d2", "c2", "b2", "a2",
    # "h1", "g1", "f1", "e1", "d1", "c1", "b1", "a1",
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

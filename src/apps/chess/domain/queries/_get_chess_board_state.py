import chess

from ..helpers import pieces_view_from_chess_board
from ..types import ChessBoardState, PiecesIdPerSquare

# Useful for quick tests:
_FEN_WHITE_ABOUT_TO_PROMOTE = "rn1qkbnr/p1P2ppp/b2p4/1p2p3/8/1P6/P1P1PPPP/RNBQKBNR w KQkq - 0 6"
_FEN_WHITE_ABOUT_TO_EN_PASSANT = "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
_FEN_BLACK_ABOUT_TO_MOVE_KING = "r1b1kb1r/ppp1qppp/2np1n2/3P4/8/2N1BN2/PPP2PPP/R2QKB1R w KQkq - 2 7"

_STARTING_FEN = chess.STARTING_FEN
_STARTING_BOARD = chess.Board(fen=_STARTING_FEN)
_STARTING_PIECES_IDS_PER_SQUARE: PiecesIdPerSquare = {
    square_name: square_name
    for square_name in [chess.square_name(square) for square, piece in _STARTING_BOARD.piece_map().items()]
}
_STARTING_PIECES_VIEW = pieces_view_from_chess_board(_STARTING_BOARD, _STARTING_PIECES_IDS_PER_SQUARE)


def get_chess_board_state(
    *, fen: str | None = None, pieces_ids_per_square: PiecesIdPerSquare | None = None
) -> ChessBoardState:
    blank_one = fen is None
    board = chess.Board(fen=_STARTING_FEN if blank_one else fen)

    return ChessBoardState(
        fen=board.fen(),
        active_player="w" if board.turn else "b",
        pieces_view=_STARTING_PIECES_VIEW if blank_one else pieces_view_from_chess_board(board, pieces_ids_per_square),
    )

from typing import NamedTuple
from django.core.exceptions import SuspiciousOperation
import chess

from ..types import SquareName, ChessBoardState
from ..helpers import KINGS_CASTLING, ROOK_SQUARE_AFTER_CASTLING, pieces_view_from_chess_board

class PieceMovementResult(NamedTuple):
    board: chess.Board
    board_state: ChessBoardState
    is_promotion: bool

def game_move_piece(*, board_state: ChessBoardState, from_square: SquareName, to_square:SquareName)->PieceMovementResult:
    board = chess.Board(fen=board_state.fen)
    current_piece = board.piece_at(chess.parse_square(from_square))
    if not current_piece:
        raise SuspiciousOperation()
    current_piece_id = board_state.pieces_id_per_square[from_square]
    targeted_piece = board.piece_at(chess.parse_square(to_square))
    print(
        f"board.turn={'white' if board.turn else 'black'} "
        f":: move_piece_to({to_square=}) "
        f":: from {from_square} :: {current_piece_id=} {targeted_piece=}"
    )
    is_promotion = current_piece.piece_type == chess.PAWN and to_square[1] in ("1", "8") 

    # @link https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
    # @link https://en.wikipedia.org/wiki/Universal_Chess_Interface
    move_uci_piece_symbol = "".join(
        [
            "",  # """ if current_piece.piece_type == chess.PAWN else current_piece.symbol().upper(),
            from_square,
            "",  # """ if targeted_piece is None else "x",
            to_square,
            # Promotion to Queen?
            "q" if is_promotion else "",
        ]
    )
    print(f"{move_uci_piece_symbol=}")
    previous_castling_rights = board.castling_rights
    board.push_uci(move_uci_piece_symbol)

    pieces_id_per_square = board_state.pieces_id_per_square

    del pieces_id_per_square[from_square]
    pieces_id_per_square[to_square] = current_piece_id

    # Specific cases:
    if current_piece.piece_type == chess.KING and board.castling_rights != previous_castling_rights:
        king_movement = (from_square, to_square)
        if king_movement in KINGS_CASTLING:
            # Our King just castled!
            # We also have to update the Rook's data in our `pieces_id_per_square` mapping
            target_rook_previous_square, target_rook_new_square = ROOK_SQUARE_AFTER_CASTLING[to_square]
            target_rook_id = board.pieces_id_per_square[target_rook_previous_square]
            board.pieces_id_per_square[target_rook_new_square] = target_rook_id
            del board.pieces_id_per_square[target_rook_previous_square]

    # if targeted_piece:
    #     self.captured_pieces[self.active_player].append(targeted_piece.symbol())

    new_board_state = ChessBoardState(
        fen=board.fen(),
        active_player="w" if board.turn else "b",
        pieces_view=pieces_view_from_chess_board(board, pieces_id_per_square),
        selected_piece_square = None,
    )

    return PieceMovementResult(
    board=board,
    board_state=new_board_state,
    is_promotion=is_promotion
    )

    # self.fen = board.fen()
    # print(f"{self.fen=}")
    # self.active_player = "w" if board.turn else "b"
    # self.pieces_view = pieces_view_from_chess_board(board, self.pieces_id_per_square)
    # self.selected_piece_square = None
    # self.selected_piece_available_targets = []
    # self._calculate_score()

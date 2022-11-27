from django_unicorn.components import UnicornView
import chess

from ...domain import PiecesView, SquareName, PieceId, PieceIdsPerSquare, PlayerCode
from ...view_helpers import pieces_view_from_chess_board, ROOK_SQUARE_AFTER_CASTLING

# Useful for quick tests:
_FEN_WHITE_ABOUT_TO_PROMOTE = "rn1qkbnr/p1P2ppp/b2p4/1p2p3/8/1P6/P1P1PPPP/RNBQKBNR w KQkq - 0 6"
_FEN_WHITE_ABOUT_TO_EN_PASSANT = "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"

_STARTING_FEN = chess.STARTING_FEN
_STARTING_BOARD = chess.Board(fen=_STARTING_FEN)
_STARTING_PIECES_IDS_PER_SQUARE = {
    square_name: square_name
    for square_name in [chess.square_name(square) for square, piece in _STARTING_BOARD.piece_map().items()]
}
_STARTING_PIECES_VIEW = pieces_view_from_chess_board(_STARTING_BOARD, _STARTING_PIECES_IDS_PER_SQUARE)


class ChessBoardView(UnicornView):
    fen = _STARTING_FEN
    pieces_view: PiecesView = _STARTING_PIECES_VIEW
    pieces_id_per_square: PieceIdsPerSquare = _STARTING_PIECES_IDS_PER_SQUARE
    active_player: PlayerCode = "w"
    selected_piece_square: SquareName | None = None
    selected_piece_available_targets: list[SquareName] = []

    def select_piece(self, square: SquareName):
        self.selected_piece_square = square
        square_index = chess.parse_square(square)
        print(f"select_piece({square=})  :: {square_index=}")
        self.selected_piece_available_targets = []
        board = self._board_from_current_fen()
        print(f"board.turn={'white' if board.turn else 'black'}")
        for move in board.legal_moves:
            if move.from_square == square_index:
                self.selected_piece_available_targets.append(chess.square_name(move.to_square))

    def move_piece_to(self, target_square: SquareName):
        assert self.selected_piece_square is not None
        board = self._board_from_current_fen()
        current_piece = board.piece_at(chess.parse_square(self.selected_piece_square))
        current_piece_id = self.pieces_id_per_square[self.selected_piece_square]
        targeted_piece = board.piece_at(chess.parse_square(target_square))
        print(
            f"move_piece_to({target_square=}) :: from {self.selected_piece_square} :: {current_piece_id=} {targeted_piece=}"
        )
        # @link https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
        # @link https://en.wikipedia.org/wiki/Universal_Chess_Interface
        move_uci_piece_symbol = "".join(
            [
                "",  # """ if current_piece.piece_type == chess.PAWN else current_piece.symbol().upper(),
                self.selected_piece_square,
                "",  # """ if targeted_piece is None else "x",
                target_square,
                # Promotion to Queen?
                "q" if current_piece.piece_type == chess.PAWN and target_square[1] in ("1", "8") else "",
            ]
        )
        print(f"{move_uci_piece_symbol=}")
        previous_castling_rights = board.castling_rights
        board.push_uci(move_uci_piece_symbol)

        del self.pieces_id_per_square[self.selected_piece_square]
        self.pieces_id_per_square[target_square] = current_piece_id

        # Specific cases:
        if current_piece.piece_type == chess.KING and board.castling_rights != previous_castling_rights:
            # Our King just castled!
            # We also have to update the Rook's data in our `pieces_id_per_square` mapping
            target_rook_previous_square, target_rook_new_square = ROOK_SQUARE_AFTER_CASTLING[target_square]
            target_rook_id = self.pieces_id_per_square[target_rook_previous_square]
            self.pieces_id_per_square[target_rook_new_square] = target_rook_id
            del self.pieces_id_per_square[target_rook_previous_square]

        self.fen = board.fen()
        print(f"{self.fen=}")
        self.active_player = "w" if board.turn else "b"
        self.pieces_view = pieces_view_from_chess_board(board, self.pieces_id_per_square)
        self.selected_piece_square = None
        self.selected_piece_available_targets = []

    def rendered(self, html: str):
        self.call("updateChessBoardsSize")

    def _board_from_current_fen(self) -> chess.Board:
        return chess.Board(fen=self.fen)

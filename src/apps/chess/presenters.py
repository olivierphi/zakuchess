from functools import cache, cached_property
from typing import TYPE_CHECKING, cast

import chess

from .domain.consts import PIECES_VALUES, PLAYER_SIDES, STARTING_PIECES
from .domain.helpers import square_from_int
from .domain.queries import get_piece_available_targets, get_team_members_by_role_by_side
from .domain.types import PieceId, PieceRole, PiecesView, PieceSymbol, PlayerSide, Square

if TYPE_CHECKING:
    from chess import Piece
    from .domain.types import TeamMemberRole, PieceView

from .models import Game, TeamMember

# Presenters are the objects we pass to our templates.


class GamePresenter:
    def __init__(
        self,
        *,
        game: Game,
        my_side: PlayerSide,
        selected_square: Square | None = None,
        selected_piece_square: Square | None = None,
        target_to_confirm: Square | None = None,
    ):
        self._game = game
        self._chess_board = chess.Board(fen=game.fen)
        self.my_side = my_side

        if selected_square is not None:
            self.selected_square = SelectedSquarePresenter(
                game_presenter=self,
                chess_board=self._chess_board,
                square=selected_square,
            )
        if selected_piece_square is not None:
            self.selected_piece = SelectedPiecePresenter(
                game_presenter=self,
                chess_board=self._chess_board,
                piece_square=selected_piece_square,
                target_to_confirm=target_to_confirm,
            )
        else:
            self.selected_piece = None

    @cached_property
    def is_my_turn(self) -> bool:
        return self.my_side == self.active_player

    @cached_property
    def board_state(self) -> str:
        # TODO: create a dedicated type for these states (Enum/Literal, doesn't matter ^^)
        if self.is_my_turn:
            if self.selected_piece is None:
                return "waiting_for_player_selection"
            if self.selected_piece.target_to_confirm is None:
                return "waiting_for_player_target_choice"
            return "waiting_for_player_target_choice_confirmation"
        if self.is_bot_turn:
            return "waiting_for_bot_turn"

    # Properties derived from the chess board:
    @cached_property
    def fen(self) -> str:
        return self._chess_board.fen()

    @cached_property
    def is_game_over(self) -> bool:
        return self._chess_board.is_game_over()

    @cached_property
    def active_player(self) -> PlayerSide:
        return "w" if self._chess_board.turn else "b"

    @cached_property
    def squares_with_pieces_that_can_move(self) -> set[Square]:
        return set(square_from_int(move.from_square) for move in self._chess_board.legal_moves)

    @cached_property
    def captured_pieces(self) -> dict[PlayerSide, list[PieceRole]]:
        remaining_pieces = [piece.symbol() for piece in self._chess_board.piece_map().values()]
        captured_pieces: dict[PlayerSide, list[PieceRole]] = {"w": [], "b": []}
        for player_side in PLAYER_SIDES:
            for starting_piece in STARTING_PIECES[player_side]:
                if starting_piece in remaining_pieces:
                    remaining_pieces.remove(starting_piece)
                else:
                    captured_pieces[player_side].append(starting_piece)
        return captured_pieces

    @cached_property
    def score(self) -> int:
        """A negative score means the "b(lack)" player is winning, a positive value means the "w(hite) player is winning."""
        remaining_pieces = [piece.symbol() for piece in self._chess_board.piece_map().values()]
        score = 0
        for piece in remaining_pieces:
            piece_symbol = cast(PieceSymbol, piece.lower())
            if piece_symbol == "k":
                continue
            score += PIECES_VALUES[piece_symbol] * (1 if piece in STARTING_PIECES["w"] else -1)
        return score

    # Properties derived from the Game model:
    @cached_property
    def active_player_side(self) -> PlayerSide:
        return self._game.active_player

    @cached_property
    def is_bot_turn(self) -> bool:
        return self._game.is_versus_bot and self._game.active_player == self._game.bot_side

    @cached_property
    def game_id(self) -> str:
        return str(self._game.id)

    @cached_property
    def pieces_view(self) -> PiecesView:
        return self._game.pieces_view

    @cached_property
    def team_members_by_role_by_side(self) -> "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]":
        return get_team_members_by_role_by_side(game=self._game)

    @cached_property
    def pieces_id_per_square(self) -> dict[Square, PieceId]:
        return {square_name: piece["id"] for square_name, piece in self.pieces_view.items()}


class SelectedSquarePresenter:
    def __init__(
        self,
        *,
        game_presenter: GamePresenter,
        chess_board: chess.Board,
        square: Square,
    ):
        self._game_presenter = game_presenter
        self._chess_board = chess_board
        self.square = square

    @cached_property
    def team_member(self) -> TeamMember:
        return self._game_presenter.team_members_by_role_by_side[self._game_presenter.active_player][
            self._square_piece_view["id"]
        ]

    @cached_property
    def player_side(self) -> PieceSymbol:
        return "w" if self.piece_at.color else "b"

    @cached_property
    def symbol(self) -> PieceSymbol:
        return self._square_piece_view["piece"]

    @cached_property
    def _square_piece_view(self) -> "PieceView":
        return self._game_presenter.pieces_view[self.square]

    @cached_property
    def piece_at(self) -> "Piece | None":
        return self._chess_board.piece_at(chess.parse_square(self.square))


class SelectedPiecePresenter(SelectedSquarePresenter):
    def __init__(
        self,
        *,
        game_presenter: GamePresenter,
        chess_board: chess.Board,
        piece_square: Square,
        target_to_confirm: Square | None,
    ):
        super().__init__(game_presenter=game_presenter, chess_board=chess_board, square=piece_square)
        self.target_to_confirm = target_to_confirm

    @cached_property
    def available_targets(self) -> set[Square]:
        return get_piece_available_targets(chess_board=self._chess_board, piece_square=self.square)

    @cache
    def is_potential_capture(self, square: Square) -> bool:
        return square in self.available_targets and self.piece_at is not None

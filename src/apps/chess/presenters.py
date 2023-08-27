from functools import cache, cached_property
from typing import TYPE_CHECKING, cast

import chess

from .domain.chess_logic import calculate_piece_available_targets
from .domain.consts import PIECES_VALUES, PLAYER_SIDES, STARTING_PIECES
from .domain.helpers import (
    get_active_player_from_chess_board,
    square_from_int,
    symbol_from_piece_role,
    team_member_role_from_piece_role,
    type_from_piece_symbol,
    player_side_from_piece_role,
)
from .domain.queries import get_team_members_by_role_by_side

if TYPE_CHECKING:
    from .domain.types import (
        PieceRoleBySquare,
        Square,
        PlayerSide,
        PieceSymbol,
        GamePhase,
        PieceRole,
        PieceType,
        TeamMemberRole,
        Factions,
        Faction,
    )

from .models import Game, TeamMember

# Presenters are the objects we pass to our templates.


class GamePresenter:
    def __init__(
        self,
        *,
        game: Game,
        my_side: "PlayerSide",
        factions: "Factions",
        selected_square: "Square | None" = None,
        selected_piece_square: "Square | None" = None,
        target_to_confirm: "Square | None" = None,
    ):
        self._game = game
        self._chess_board = chess.Board(fen=game.fen)
        self.my_side = my_side
        self.factions = factions

        if selected_square is not None:
            self.selected_square = SelectedSquarePresenter(
                game_presenter=self,
                chess_board=self._chess_board,
                square=selected_square,
            )

        self.selected_piece: SelectedPiecePresenter | None = None
        if selected_piece_square is not None:
            self.selected_piece = SelectedPiecePresenter(
                game_presenter=self,
                chess_board=self._chess_board,
                piece_square=selected_piece_square,
                target_to_confirm=target_to_confirm,
            )

    @cached_property
    def turn_number(self) -> int:
        return self._chess_board.fullmove_number

    @cached_property
    def is_my_turn(self) -> bool:
        return self.my_side == self.active_player

    @cached_property
    def game_phase(self) -> "GamePhase":
        if self.is_my_turn:
            if self.selected_piece is None:
                return "waiting_for_player_selection"
            if self.selected_piece.target_to_confirm is None:
                return "waiting_for_player_target_choice"
            return "waiting_for_player_target_choice_confirmation"
        if self.is_bot_turn:
            return "waiting_for_bot_turn"

        return "waiting_for_opponent_turn"

    # Properties derived from the chess board:
    @cached_property
    def fen(self) -> str:
        return self._chess_board.fen()

    @cached_property
    def is_game_over(self) -> bool:
        return self._chess_board.is_game_over()

    @cached_property
    def active_player(self) -> "PlayerSide":
        return get_active_player_from_chess_board(self._chess_board)

    @cached_property
    def squares_with_pieces_that_can_move(self) -> set["Square"]:
        return set(square_from_int(move.from_square) for move in self._chess_board.legal_moves)

    @cached_property
    def piece_faction(self, piece: "PieceRole") -> "Faction":
        return self.factions[player_side_from_piece_role(piece)]

    @cached_property
    def captured_pieces(self) -> dict["PlayerSide", list["PieceType"]]:
        remaining_pieces = [piece.symbol() for piece in self._chess_board.piece_map().values()]
        captured_pieces: dict["PlayerSide", list["PieceType"]] = {"w": [], "b": []}
        for player_side in PLAYER_SIDES:
            for starting_piece in STARTING_PIECES[player_side]:
                if starting_piece in remaining_pieces:
                    remaining_pieces.remove(starting_piece)
                else:
                    captured_pieces[player_side].append(type_from_piece_symbol(starting_piece))
        for player_side in captured_pieces.keys():
            captured_pieces[player_side].sort(key=lambda piece_type: -PIECES_VALUES[piece_type])
        return captured_pieces

    @cached_property
    def score(self) -> int:
        """A negative score means the "b(lack)" player is winning, a positive value means the "w(hite) player is winning."""
        remaining_pieces = [piece.symbol() for piece in self._chess_board.piece_map().values()]
        score = 0
        for piece in remaining_pieces:
            piece_symbol = cast("PieceType", piece.lower())
            if piece_symbol == "k":
                continue
            score += PIECES_VALUES[piece_symbol] * (1 if piece in STARTING_PIECES["w"] else -1)
        return score

    # Properties derived from the Game model:
    @cached_property
    def active_player_side(self) -> "PlayerSide":
        return cast("PlayerSide", self._game.active_player)  # TODO: this cast shouldn't be required ¯\_(ツ)_/¯

    @cached_property
    def is_bot_turn(self) -> bool:
        return self._game.is_versus_bot and self._game.active_player == self._game.bot_side

    @cached_property
    def game_id(self) -> str:
        return str(self._game.id)

    @cached_property
    def piece_role_by_square(self) -> "PieceRoleBySquare":
        return self._game.piece_role_by_square

    @cached_property
    def team_members_by_role_by_side(self) -> "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]":
        return get_team_members_by_role_by_side(game=self._game)


class SelectedSquarePresenter:
    def __init__(
        self,
        *,
        game_presenter: GamePresenter,
        chess_board: chess.Board,
        square: "Square",
    ):
        self._game_presenter = game_presenter
        self._chess_board = chess_board
        self.square = square

    @cached_property
    def team_member(self) -> "TeamMember":
        player_side = (
            self._game_presenter.selected_piece.player_side
            if self._game_presenter.selected_piece
            else self._game_presenter.active_player_side
        )
        return self._game_presenter.team_members_by_role_by_side[player_side][
            team_member_role_from_piece_role(self.piece_role)
        ]

    @cached_property
    def player_side(self) -> "PlayerSide":
        return "w" if self.piece_at.color else "b"

    @cached_property
    def symbol(self) -> "PieceSymbol":
        return symbol_from_piece_role(self.piece_role)

    @cached_property
    def piece_role(self) -> "PieceRole":
        return self._game_presenter.piece_role_by_square[self.square]

    @cached_property
    def piece_at(self) -> "chess.Piece":
        return cast("chess.Piece", self._chess_board.piece_at(chess.parse_square(self.square)))


class SelectedPiecePresenter(SelectedSquarePresenter):
    def __init__(
        self,
        *,
        game_presenter: GamePresenter,
        chess_board: chess.Board,
        piece_square: "Square",
        target_to_confirm: "Square | None",
    ):
        super().__init__(game_presenter=game_presenter, chess_board=chess_board, square=piece_square)
        self.target_to_confirm = target_to_confirm

    @cached_property
    def available_targets(self) -> frozenset["Square"]:
        return calculate_piece_available_targets(chess_board=self._chess_board, piece_square=self.square)

    @cache
    def is_potential_capture(self, square: "Square") -> bool:
        return square in self.available_targets and self.piece_at is not None

from functools import cache, cached_property
from typing import TYPE_CHECKING, cast

import chess

from .business_logic import get_daily_challenge_turns_state
from .business_logic.consts import PLAYER_SIDES
from .business_logic.daily_challenge import MAXIMUM_TURNS_PER_CHALLENGE
from .chess_logic import calculate_piece_available_targets
from .helpers import (
    chess_lib_color_to_player_side,
    get_active_player_side_from_chess_board,
    player_side_from_piece_role,
    square_from_int,
    symbol_from_piece_role,
    team_member_role_from_piece_role,
)
from .models import DailyChallenge

if TYPE_CHECKING:
    from .business_logic.daily_challenge import ChallengeTurnsState, PlayerGameState
    from .business_logic.types import (
        Factions,
        GamePhase,
        PieceRole,
        PieceRoleBySquare,
        PieceSymbol,
        PlayerSide,
        Square,
        TeamMember,
        TeamMemberRole,
    )


# Presenters are the objects we pass to our templates.


class GamePresenter:
    def __init__(
        self,
        *,
        challenge: DailyChallenge,
        game_state: "PlayerGameState",
        forced_bot_move: tuple["Square", "Square"] | None = None,
        selected_square: "Square | None" = None,
        selected_piece_square: "Square | None" = None,
        target_to_confirm: "Square | None" = None,
        restart_daily_challenge_ask_confirmation: bool = False,
        is_bot_move: bool = False,
    ):
        self._challenge = challenge
        self.game_state = game_state
        self.forced_bot_move = forced_bot_move
        self.restart_daily_challenge_ask_confirmation = (
            restart_daily_challenge_ask_confirmation
        )
        self.is_bot_move = is_bot_move

        self._chess_board = chess.Board(fen=game_state["fen"])
        self._piece_role_by_square = game_state["piece_role_by_square"]

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
    def is_my_turn(self) -> bool:
        return self._challenge.my_side == self.active_player

    @cached_property
    def challenge_turns_state(self) -> "ChallengeTurnsState":
        return get_daily_challenge_turns_state(self.game_state)

    @property
    def challenge_turns_counter(self) -> int:
        return self.game_state["turns_counter"]

    @property
    def challenge_total_turns(self) -> int:
        return MAXIMUM_TURNS_PER_CHALLENGE

    @cached_property
    def game_phase(self) -> "GamePhase":
        if self.challenge_turns_state.game_over:
            return "game_over:lost"
        if (winner := self.winner) is not None:
            return (
                "game_over:won"
                if winner == self._challenge.my_side
                else "game_over:lost"
            )
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
    def is_check(self) -> bool:
        return self._chess_board.is_check()

    @cached_property
    def is_game_over(self) -> bool:
        if self.challenge_turns_state.game_over:
            return True
        return self.winner is not None

    @cached_property
    def winner(self) -> "PlayerSide | None":
        return (
            None
            if (outcome := self._chess_board.outcome()) is None
            else chess_lib_color_to_player_side(outcome.winner)
        )

    @cached_property
    def active_player(self) -> "PlayerSide":
        return get_active_player_side_from_chess_board(self._chess_board)

    @cached_property
    def squares_with_pieces_that_can_move(self) -> set["Square"]:
        return set(
            square_from_int(move.from_square) for move in self._chess_board.legal_moves
        )

    # Properties derived from the Game model:
    @cached_property
    def active_player_side(self) -> "PlayerSide":
        return chess_lib_color_to_player_side(self._chess_board.turn)

    @cached_property
    def is_player_turn(self) -> bool:
        return self.active_player_side != self._challenge.bot_side

    @cached_property
    def is_bot_turn(self) -> bool:
        return self.active_player_side == self._challenge.bot_side

    @cached_property
    def game_id(self) -> str:
        return str(self._challenge.id)

    @cached_property
    def factions(self) -> "Factions":
        return self._challenge.factions

    @cached_property
    def piece_role_by_square(self) -> "PieceRoleBySquare":
        return self._piece_role_by_square

    @cache
    def piece_role_at_square(self, square: "Square") -> "PieceRole":
        return self._piece_role_by_square[square]

    @cached_property
    def team_members_by_role_by_side(
        self,
    ) -> "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]":
        result: "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]" = {}
        for player_side in PLAYER_SIDES:
            result[player_side] = {}
            for team_member in self._challenge.teams[player_side]:
                member_role = team_member_role_from_piece_role(team_member["role"])
                result[player_side][member_role] = team_member
        return result


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
        return player_side_from_piece_role(
            self._game_presenter.piece_role_at_square(self.square)
        )

    @cached_property
    def symbol(self) -> "PieceSymbol":
        return symbol_from_piece_role(self.piece_role)

    @cached_property
    def piece_role(self) -> "PieceRole":
        return self._game_presenter.piece_role_by_square[self.square]

    @cached_property
    def piece_at(self) -> "chess.Piece":
        return cast(
            "chess.Piece", self._chess_board.piece_at(chess.parse_square(self.square))
        )

    def __str__(self) -> str:
        return f"{self.square} (piece role: {self.piece_role})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)})>"


class SelectedPiecePresenter(SelectedSquarePresenter):
    def __init__(
        self,
        *,
        game_presenter: GamePresenter,
        chess_board: chess.Board,
        piece_square: "Square",
        target_to_confirm: "Square | None",
    ):
        super().__init__(
            game_presenter=game_presenter, chess_board=chess_board, square=piece_square
        )
        self.target_to_confirm = target_to_confirm

    @cached_property
    def available_targets(self) -> frozenset["Square"]:
        chess_board_active_player_side = chess_lib_color_to_player_side(
            self._chess_board.turn
        )
        square_index = chess.parse_square(self.square)
        piece_player_side = chess_lib_color_to_player_side(
            self._chess_board.color_at(square_index)
        )
        if chess_board_active_player_side != piece_player_side:
            # Let's pretend it's that player's turn, so we can calculate the available targets:
            chess_board = self._chess_board.copy()
            chess_board.turn = not chess_board.turn
        else:
            chess_board = self._chess_board
        return calculate_piece_available_targets(
            chess_board=chess_board, piece_square=self.square
        )

    @cache
    def is_potential_capture(self, square: "Square") -> bool:
        return square in self.available_targets and self.piece_at is not None

    def __str__(self) -> str:
        return f"{self.piece_role} at {self.square}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)})>"

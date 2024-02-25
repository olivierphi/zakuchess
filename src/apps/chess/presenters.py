from abc import ABC, abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple, cast

import chess

from apps.chess.business_logic import calculate_piece_available_targets

from .consts import PLAYER_SIDES
from .helpers import (
    chess_lib_color_to_player_side,
    chess_lib_square_to_square,
    get_active_player_side_from_chess_board,
    player_side_from_piece_role,
    player_side_from_piece_symbol,
    symbol_from_piece_role,
    team_member_role_from_piece_role,
)
from .models import UserPrefs
from .types import ChessInvalidStateException

if TYPE_CHECKING:
    from dominate.util import text

    from .types import (
        FEN,
        Factions,
        GamePhase,
        GameTeams,
        PieceRole,
        PieceRoleBySquare,
        PieceSymbol,
        PieceType,
        PlayerSide,
        Square,
        TeamMember,
        TeamMemberRole,
    )


# Presenters are the objects we pass to our templates.

_PIECES_VALUES: dict["PieceType", int] = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
}


class GamePresenter(ABC):
    """
    Such a presenter is passed to our HTML rendering layer: it exposes the chess logic
    we need to display the game in its current state.
    The presenter only exposes data for a given immutable state of the game, which is
    why many of its properties are cached.
    """

    def __init__(
        self,
        *,
        fen: "FEN",
        piece_role_by_square: "PieceRoleBySquare",
        teams: "GameTeams",
        refresh_last_move: bool,
        is_htmx_request: bool,
        selected_square: "Square | None" = None,
        selected_piece_square: "Square | None" = None,
        target_to_confirm: "Square | None" = None,
        forced_bot_move: tuple["Square", "Square"] | None = None,
        force_square_info: bool = False,
        last_move: tuple["Square", "Square"] | None = None,
        captured_piece_role: "PieceRole | None" = None,
        is_preview: bool = False,
        user_prefs: UserPrefs | None = None,
    ):
        self._fen = fen
        self._chess_board = chess.Board(fen=fen)
        self._piece_role_by_square = piece_role_by_square
        self._teams = teams

        self.forced_bot_move = forced_bot_move
        self.refresh_last_move = refresh_last_move
        self.is_htmx_request = is_htmx_request
        self.force_square_info = force_square_info
        self.last_move = last_move
        self.captured_piece_role = captured_piece_role
        self.is_preview = is_preview
        self.user_prefs = user_prefs or UserPrefs()

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

    @property
    @abstractmethod
    def urls(self) -> "GamePresenterUrls": ...

    @property
    @abstractmethod
    def is_my_turn(self) -> bool: ...

    @property
    @abstractmethod
    def game_phase(self) -> "GamePhase": ...

    # Properties derived from the chess board:
    @cached_property
    def fen(self) -> str:
        return self._chess_board.fen()

    @cached_property
    def is_check(self) -> bool:
        return self._chess_board.is_check()

    @cached_property
    def is_game_over(self) -> bool:
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
            chess_lib_square_to_square(move.from_square)
            for move in self._chess_board.legal_moves
        )

    # Properties derived from the Game model:
    @cached_property
    def active_player_side(self) -> "PlayerSide":
        return chess_lib_color_to_player_side(self._chess_board.turn)

    @property
    def can_select_pieces(self) -> bool:
        return True

    @property
    @abstractmethod
    def is_player_turn(self) -> bool: ...

    @property
    @abstractmethod
    def is_bot_turn(self) -> bool: ...

    @property
    @abstractmethod
    def solution_index(self) -> int | None: ...

    @property
    @abstractmethod
    def game_id(self) -> str: ...

    @property
    @abstractmethod
    def factions(self) -> "Factions": ...

    @property
    @abstractmethod
    def is_intro_turn(self) -> bool: ...

    @property
    @abstractmethod
    def player_side_to_highlight_all_pieces_for(self) -> "PlayerSide | None": ...

    @property
    @abstractmethod
    def speech_bubble(self) -> "SpeechBubbleData | None": ...

    @cached_property
    def piece_role_by_square(self) -> "PieceRoleBySquare":
        return self._piece_role_by_square

    def piece_role_at_square(self, square: "Square") -> "PieceRole":
        try:
            return self._piece_role_by_square[square]
        except KeyError as exc:
            raise ChessInvalidStateException(f"No piece at square {square}") from exc

    @cached_property
    def team_members_by_role_by_side(
        self,
    ) -> "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]":
        result: "dict[PlayerSide, dict[TeamMemberRole, TeamMember]]" = {}
        for player_side in PLAYER_SIDES:
            result[player_side] = {}
            for team_member in self._teams[player_side]:
                member_role = team_member_role_from_piece_role(team_member["role"])
                result[player_side][member_role] = team_member
        return result

    @cached_property
    def naive_score(self) -> int:
        """
        A negative score means the "b(lack)" player is winning,
        while a positive value means the "w(hite) player is winning.
        This is a very naive score, only based on the value of pieces left on each side.
        """
        remaining_pieces = cast(
            "list[PieceSymbol]",
            [piece.symbol() for piece in self._chess_board.piece_map().values()],
        )
        score = 0
        for piece in remaining_pieces:
            piece_symbol = cast("PieceType", piece.lower())
            if piece_symbol == "k":
                continue
            multiplier = 1 if player_side_from_piece_symbol(piece) == "w" else -1
            score += _PIECES_VALUES[piece_symbol] * multiplier
        return score

    @property
    def chess_board(self) -> chess.Board:
        return self._chess_board


class GamePresenterUrls(ABC):
    def __init__(self, *, game_presenter: GamePresenter):
        self._game_presenter = game_presenter

    def htmx_game_no_selection_url(self, *, board_id: str) -> str:
        raise NotImplementedError

    def htmx_game_select_piece_url(self, *, square: "Square", board_id: str) -> str:
        raise NotImplementedError

    def htmx_game_move_piece_url(self, *, square: "Square", board_id: str) -> str:
        raise NotImplementedError

    def htmx_game_play_bot_move_url(self, *, board_id: str) -> str:
        raise NotImplementedError

    def htmx_game_play_solution_move_url(self, *, board_id: str) -> str:
        raise NotImplementedError


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
        return cast("chess.Piece", self._chess_board.piece_at(self._chess_lib_square))

    @cached_property
    def _chess_lib_square(self) -> chess.Square:
        return chess.parse_square(self.square)

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
            game_presenter=game_presenter,
            chess_board=chess_board,
            square=piece_square,
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
            # Let's pretend it's that player's turn,
            # so we can calculate the available targets:
            chess_board = self._chess_board.copy()
            chess_board.turn = not chess_board.turn
        else:
            chess_board = self._chess_board

        return calculate_piece_available_targets(
            chess_board=chess_board, piece_square=self.square
        )

    def is_potential_capture(self, square: "Square") -> bool:
        return square in self.available_targets and self.piece_at is not None

    @cached_property
    def is_pinned(self) -> bool:
        return self._chess_board.is_pinned(
            self.piece_at.color,
            self._chess_lib_square,
        )

    def __str__(self) -> str:
        return f"{self.piece_role} at {self.square}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)})>"


class SpeechBubbleData(NamedTuple):
    text: "str | text"
    square: "Square"
    time_out: float | None = None  # if it's None, should be expressed in seconds
    character_display: "PieceRole | None" = None

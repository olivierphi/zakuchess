from functools import cached_property
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.urls import reverse

from apps.chess.helpers import uci_move_squares
from apps.chess.presenters import GamePresenter, GamePresenterUrls, SpeechBubbleData

from .business_logic import get_speech_bubble
from .models import DailyChallenge

if TYPE_CHECKING:
    import chess

    from apps.chess.models import UserPrefs
    from apps.chess.types import Factions, GamePhase, PieceRole, PlayerSide, Square

    from .models import PlayerGameState

# Presenters are the objects we pass to our templates.


class DailyChallengeGamePresenter(GamePresenter):
    def __init__(
        self,
        *,
        challenge: DailyChallenge,
        game_state: "PlayerGameState",
        refresh_last_move: bool,
        is_htmx_request: bool,
        forced_bot_move: tuple["Square", "Square"] | None = None,
        forced_speech_bubble: tuple["Square", str] | None = None,
        selected_square: "Square | None" = None,
        selected_piece_square: "Square | None" = None,
        target_to_confirm: "Square | None" = None,
        is_bot_move: bool = False,
        force_square_info: bool = False,
        captured_team_member_role: "PieceRole | None" = None,
        just_won: bool = False,
        is_preview: bool = False,
        is_very_first_game: bool = False,
        user_prefs: "UserPrefs | None" = None,
    ):
        # A published challenge always has a `teams` non-null field:
        assert challenge.teams

        super().__init__(
            fen=game_state.fen,
            piece_role_by_square=game_state.piece_role_by_square,
            teams=challenge.teams,
            refresh_last_move=refresh_last_move,
            is_htmx_request=is_htmx_request,
            selected_square=selected_square,
            selected_piece_square=selected_piece_square,
            target_to_confirm=target_to_confirm,
            forced_bot_move=forced_bot_move,
            last_move=self._last_move_from_game_state(game_state),
            force_square_info=force_square_info,
            captured_piece_role=captured_team_member_role,
            is_preview=is_preview,
            bot_depth=challenge.bot_depth,
            user_prefs=user_prefs,
        )
        self._challenge = challenge
        self.game_state = game_state
        self.is_bot_move = is_bot_move
        self.just_won = just_won
        self.is_very_first_game = is_very_first_game
        self._forced_speech_bubble = forced_speech_bubble

    @cached_property
    def urls(self) -> "DailyChallengeGamePresenterUrls":
        return DailyChallengeGamePresenterUrls(game_presenter=self)

    @cached_property
    def is_my_turn(self) -> bool:
        return self._challenge.my_side == self.active_player

    @cached_property
    def challenge_current_attempt_turns_counter(self) -> int:
        return self.game_state.current_attempt_turns_counter

    @cached_property
    def challenge_total_turns_counter(self) -> int:
        return self.game_state.turns_counter

    @cached_property
    def challenge_solution_turns_count(self) -> int:
        return self._challenge.solution_turns_count

    @cached_property
    def challenge_attempts_counter(self) -> int:
        return self.game_state.attempts_counter

    @cached_property
    def game_phase(self) -> "GamePhase":
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

    @property
    def can_select_pieces(self) -> bool:
        # During the bot's turn we're not allowed to select any piece, as we're waiting
        # for the delayed HTMX request to play the bot's move.
        return self.is_player_turn and not self.is_game_over

    @cached_property
    def is_player_turn(self) -> bool:
        return self.active_player_side != self._challenge.bot_side

    @cached_property
    def is_bot_turn(self) -> bool:
        return self.active_player_side == self._challenge.bot_side

    @cached_property
    def solution_index(self) -> int | None:
        return self.game_state.solution_index

    @cached_property
    def game_id(self) -> str:
        return str(self._challenge.id)

    @cached_property
    def factions(self) -> "Factions":
        return self._challenge.factions

    @cached_property
    def is_intro_turn(self) -> bool:
        return (
            self.is_bot_move
            and self.challenge_attempts_counter == 0
            and self.challenge_current_attempt_turns_counter == 0
        )

    @cached_property
    def is_player_move(self) -> bool:
        return not self.is_bot_move

    @cached_property
    def player_side_to_highlight_all_pieces_for(self) -> "PlayerSide | None":
        if self.is_intro_turn:
            return self._challenge.my_side
        return None

    @cached_property
    def speech_bubble(self) -> SpeechBubbleData | None:
        return get_speech_bubble(self)

    @property
    def chess_board(self) -> "chess.Board":
        return self._chess_board

    @property
    def challenge(self) -> DailyChallenge:
        return self._challenge

    @property
    def forced_speech_bubble(self) -> tuple["Square", str] | None:
        return self._forced_speech_bubble

    @staticmethod
    def _last_move_from_game_state(
        game_state: "PlayerGameState",
    ) -> tuple["Square", "Square"] | None:
        if (moves := game_state.moves) and len(moves) >= 4:
            return uci_move_squares(moves[-4:])
        return None


class DailyChallengeGamePresenterUrls(GamePresenterUrls):
    def htmx_game_no_selection_url(self, *, board_id: str) -> str:
        return "".join(
            (
                reverse("daily_challenge:htmx_game_no_selection"),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_select_piece_url(self, *, square: "Square", board_id: str) -> str:
        return "".join(
            (
                reverse(
                    "daily_challenge:htmx_game_select_piece",
                    kwargs={
                        "location": square,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_move_piece_url(self, *, square: "Square", board_id: str) -> str:
        assert self._game_presenter.selected_piece is not None
        return "".join(
            (
                reverse(
                    "daily_challenge:htmx_game_move_piece",
                    kwargs={
                        "from_": self._game_presenter.selected_piece.square,
                        "to": square,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_play_bot_move_url(self, *, board_id: str) -> str:
        return "".join(
            (
                # We'll use "<from>" and "<to>" as placeholders - our JS
                # code will replace them with the actual squares when it needs this URL
                # pattern.
                reverse(
                    "daily_challenge:htmx_game_bot_move",
                    kwargs={
                        "from_": "a1",
                        "to": "a2",
                    },
                )
                .replace("a1", "<from>")
                .replace("a2", "<to>"),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_play_solution_move_url(self, *, board_id: str) -> str:
        return "".join(
            (
                reverse(
                    "daily_challenge:htmx_see_daily_challenge_solution_play",
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

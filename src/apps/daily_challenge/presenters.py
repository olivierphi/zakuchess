import random
from functools import cached_property
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.urls import reverse

from apps.chess.presenters import GamePresenter, GamePresenterUrls, SpeechBubbleData

from ..chess.helpers import player_side_to_chess_lib_color, square_from_int
from .business_logic import get_daily_challenge_turns_state
from .consts import MAXIMUM_TURNS_PER_CHALLENGE
from .models import DailyChallenge

if TYPE_CHECKING:
    from apps.chess.types import Factions, GamePhase, PlayerSide, Square

    from .types import ChallengeTurnsState, PlayerGameState

# Presenters are the objects we pass to our templates.


class DailyChallengeGamePresenter(GamePresenter):
    def __init__(
        self,
        *,
        challenge: DailyChallenge,
        game_state: "PlayerGameState",
        is_htmx_request: bool,
        forced_bot_move: tuple["Square", "Square"] | None = None,
        selected_square: "Square | None" = None,
        selected_piece_square: "Square | None" = None,
        target_to_confirm: "Square | None" = None,
        restart_daily_challenge_ask_confirmation: bool = False,
        is_bot_move: bool = False,
    ):
        super().__init__(
            fen=game_state["fen"],
            piece_role_by_square=game_state["piece_role_by_square"],
            teams=challenge.teams,
            is_htmx_request=is_htmx_request,
            selected_square=selected_square,
            selected_piece_square=selected_piece_square,
            target_to_confirm=target_to_confirm,
            forced_bot_move=forced_bot_move,
        )
        self._challenge = challenge
        self.game_state = game_state
        self.restart_daily_challenge_ask_confirmation = (
            restart_daily_challenge_ask_confirmation
        )
        self.is_bot_move = is_bot_move

    @cached_property
    def urls(self) -> "DailyChallengeGamePresenterUrls":
        return DailyChallengeGamePresenterUrls(game_presenter=self)

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

    @property
    def challenge_turns_left(self) -> int:
        return self.challenge_turns_state.turns_left

    @property
    def challenge_attempts_counter(self) -> int:
        return self.challenge_turns_state.attempts_counter

    @cached_property
    def game_phase(self) -> "GamePhase":
        if self.challenge_turns_state.time_s_up:
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

    @cached_property
    def is_game_over(self) -> bool:
        if self.challenge_turns_state.time_s_up:
            return True
        return super().is_game_over

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
    def is_intro_turn(self) -> bool:
        return self.is_bot_move and self.challenge_turns_counter == 0

    @cached_property
    def player_side_to_highlight_all_pieces_for(self) -> "PlayerSide | None":
        if self.is_intro_turn:
            return self._challenge.my_side
        return None

    @cached_property
    def speech_bubble(self) -> SpeechBubbleData | None:
        if self.is_intro_turn:
            text = (
                self._challenge.intro_turn_speech_text
                or "Come on folks, we can win this one!"
            )
            return SpeechBubbleData(
                text=text, square=self._challenge.intro_turn_speech_square, time_out=8
            )

        if (
            self.is_bot_move
            and self.game_state["turns_counter"] > 1
            and self.game_state["current_attempt_turns_counter"] == 0
        ):
            return SpeechBubbleData(
                text="Let's try that again, folks! 🤞",
                square=self._challenge.intro_turn_speech_square,
            )

        if (
            self.is_player_turn
            and self.is_htmx_request
            and not self.restart_daily_challenge_ask_confirmation
            and self.naive_score < -3
        ):
            probability = 0.6 if self.naive_score < -6 else 0.3
            if random.random() > probability:
                king_square = square_from_int(
                    self._chess_board.king(
                        player_side_to_chess_lib_color(self._challenge.my_side)
                    )
                )
                return SpeechBubbleData(
                    text="We're in a tough situation, folks 😬<br>"
                    "Maybe restarting from the beginning, "
                    "by using the ↩️ button, could be a good idea?",
                    square=king_square,
                    time_out=8,
                )
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
                reverse("daily_challenge:htmx_game_select_piece"),
                "?",
                urlencode({"square": square, "board_id": board_id}),
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
                reverse("daily_challenge:htmx_game_bot_move"),
                "?",
                urlencode({"board_id": board_id, "move": "BOT_MOVE"}),
            )
        )

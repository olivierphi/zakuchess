from functools import cached_property
from typing import TYPE_CHECKING, cast
from urllib.parse import urlencode

from django.urls import reverse

from apps.chess.chess_helpers import uci_move_squares
from apps.chess.presenters import GamePresenter, GamePresenterUrls

if TYPE_CHECKING:
    from apps.chess.models import GameFactions, UserPrefs
    from apps.chess.presenters import SpeechBubbleData
    from apps.chess.types import (
        FEN,
        BoardOrientation,
        GamePhase,
        PlayerSide,
        Square,
    )

    from .models import LichessGameFullFromStreamWithMetadata


class LichessCorrespondenceGamePresenter(GamePresenter):
    def __init__(
        self,
        *,
        game_data: "LichessGameFullFromStreamWithMetadata",
        refresh_last_move: bool,
        is_htmx_request: bool,
        selected_piece_square: "Square | None" = None,
        user_prefs: "UserPrefs | None" = None,
    ):
        self._game_data = game_data

        self._chess_board = game_data.chess_board
        fen = cast("FEN", self._chess_board.fen())

        if self._game_data.moves:
            last_move = uci_move_squares(self._game_data.moves[-1])
        else:
            last_move = None

        super().__init__(
            fen=fen,
            piece_role_by_square=game_data.piece_role_by_square,
            teams=game_data.teams,
            refresh_last_move=refresh_last_move,
            is_htmx_request=is_htmx_request,
            selected_piece_square=selected_piece_square,
            last_move=last_move,
            user_prefs=user_prefs,
        )

    @cached_property
    def board_orientation(self) -> "BoardOrientation":
        return self._game_data.board_orientation

    @cached_property
    def urls(self) -> "GamePresenterUrls":
        return LichessCorrespondenceGamePresenterUrls(game_presenter=self)

    @cached_property
    def is_my_turn(self) -> bool:
        return self._game_data.players_from_my_perspective.active_player == "me"

    @cached_property
    def my_side(self) -> "PlayerSide | None":
        return self._game_data.players_from_my_perspective.me.player_side

    @cached_property
    def game_phase(self) -> "GamePhase":
        # TODO: manage "game over" situations
        if self.is_my_turn:
            if self.selected_piece is None:
                return "waiting_for_player_selection"
            if self.selected_piece.target_to_confirm is None:
                return "waiting_for_player_target_choice"
            return "waiting_for_player_target_choice_confirmation"
        return "waiting_for_opponent_turn"

    @cached_property
    def is_bot_turn(self) -> bool:
        return False  # no bots involved in Lichess correspondence games

    @property
    def solution_index(self) -> int | None:
        return None

    @cached_property
    def game_id(self) -> str:
        return self._game_data.raw_data.id

    @cached_property
    def factions(self) -> "GameFactions":
        return self._game_data.game_factions

    @property
    def is_intro_turn(self) -> bool:
        return False

    @cached_property
    def player_side_to_highlight_all_pieces_for(self) -> "PlayerSide | None":
        return None

    @cached_property
    def speech_bubble(self) -> "SpeechBubbleData | None":
        return None


class LichessCorrespondenceGamePresenterUrls(GamePresenterUrls):
    def htmx_game_no_selection_url(self, *, board_id: str) -> str:
        return "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_no_selection",
                    kwargs={
                        "game_id": self._game_presenter.game_id,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_select_piece_url(self, *, square: "Square", board_id: str) -> str:
        return "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_select_piece",
                    kwargs={
                        "game_id": self._game_presenter.game_id,
                        "location": square,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_move_piece_url(self, *, square: "Square", board_id: str) -> str:
        assert self._game_presenter.selected_piece is not None  # type checker: happy
        return "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_move_piece",
                    kwargs={
                        "game_id": self._game_presenter.game_id,
                        "from_": self._game_presenter.selected_piece.square,
                        "to": square,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_play_bot_move_url(self, *, board_id: str) -> str:
        return "#"  # TODO

    def htmx_game_play_solution_move_url(self, *, board_id: str) -> str:
        return "#"  # TODO

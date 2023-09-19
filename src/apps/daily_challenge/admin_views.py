from datetime import timedelta
from typing import TYPE_CHECKING, Literal, TypeAlias, cast

import chess
from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.timezone import now
from django.views.decorators.clickjacking import xframe_options_exempt
from dominate.util import raw

from apps.chess.business_logic import calculate_fen_before_move
from apps.chess.components.chess_board import chess_arena
from apps.utils.view_decorators import user_is_staff
from apps.webui.components.layout import page

from .business_logic import set_daily_challenge_teams_and_pieces_roles
from .cookie_helpers import clear_daily_challenge_state_in_session
from .models import DailyChallenge
from .presenters import DailyChallengeGamePresenter
from .types import PlayerGameState

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.chess.types import FEN, PieceSymbol, Square

GameUpdate: TypeAlias = tuple["Square", "PieceSymbol" | Literal["x"]]


@xframe_options_exempt
@user_passes_test(user_is_staff)
def preview_daily_challenge(request: "HttpRequest") -> HttpResponse:
    errors: dict = {}

    form = DailyChallengePreviewForm(request.GET)
    if not form.is_valid():
        errors = form.errors

    game_update = form.cleaned_data.get("game_update")
    game_presenter = _get_game_presenter(
        fen=form.cleaned_data.get("fen"),
        bot_first_move=form.cleaned_data.get("bot_first_move"),
        intro_turn_speech_square=form.cleaned_data.get("intro_turn_speech_square"),
        game_update=game_update,
    )

    return HttpResponse(
        page(
            raw("<style>header, footer { display: none; }</style>"),
            raw(
                """<pre style="white-space: pre-wrap; background-color: #0f172a; color: #f1f5f9;">"""
                "Errors:\n"
                f"{errors!r}"
                "</pre>"
            )
            if errors
            else "",
            raw(
                """<div style="background-color: #0f172a; color: #f1f5f9; text-align: center;">"""
                f"Score advantage: <b>{game_presenter.naive_score}</b></div>"
            )
            if not errors
            else "",
            raw(
                f"""<script>window.parent.document.getElementById("id_fen").value = "{game_presenter.fen}";</script>"""
            )
            if game_update
            else "",
            chess_arena(
                game_presenter=game_presenter, status_bars=[], board_id="admin"
            ),
            request=request,
        )
    )


@user_passes_test(user_is_staff)
def play_future_daily_challenge(
    request: "HttpRequest", lookup_key: str
) -> HttpResponse:
    clear_daily_challenge_state_in_session(request=request)

    response = redirect("daily_challenge:daily_game_view")
    response.set_signed_cookie(
        "admin_daily_challenge_lookup_key",
        lookup_key,
        expires=now() + timedelta(minutes=30),
    )

    return response


class DailyChallengePreviewForm(forms.Form):
    fen = forms.CharField(min_length=20, max_length=90)
    bot_first_move = forms.CharField(max_length=4, required=False)
    intro_turn_speech_square = forms.CharField(max_length=2, required=False)
    game_update = forms.CharField(min_length=4, max_length=4, required=False)

    def clean_fen(self) -> str:
        try:
            chess_board = chess.Board(fen=self.cleaned_data["fen"])
        except ValueError as exc:
            raise ValidationError(exc) from exc
        # Normalise so that the FEN always starts with the human player's turn:
        chess_board.turn = chess.WHITE
        return chess_board.fen()

    def clean_bot_first_move(self) -> str | None:
        bot_first_move = self.cleaned_data.get("bot_first_move", "")
        if len(bot_first_move) != 4:
            return None
        fen = self.cleaned_data.get("fen", "")
        if not fen:
            return None
        try:
            calculate_fen_before_move(
                fen_after_move=fen,
                move_uci=bot_first_move,
                moving_player_side="b",
            )
        except ValueError as exc:
            raise ValidationError(exc) from exc
        return bot_first_move

    def clean_intro_turn_speech_square(self) -> "Square | None":
        intro_turn_speech_square = self.cleaned_data.get("intro_turn_speech_square", "")
        if len(intro_turn_speech_square) != 2:
            return None
        fen = self.cleaned_data.get("fen", "")
        if not fen:
            return None
        chess_board = chess.Board(fen=self.cleaned_data["fen"])
        piece_at_square = chess_board.piece_at(
            chess.parse_square(intro_turn_speech_square)
        )
        if not piece_at_square or piece_at_square.color != chess.WHITE:
            raise ValidationError(
                f"'{intro_turn_speech_square}' is not a valid 'w' square"
            )
        return intro_turn_speech_square

    def clean_game_update(self) -> GameUpdate | None:
        try:
            square, piece = self.cleaned_data.get("game_update").split(":")
        except ValueError:
            return None
        if not all((square, piece)):
            return None
        try:
            chess.parse_square(square)
        except ValueError as exc:
            raise ValidationError(f"'{square}' is not a valid square") from exc
        # fmt: off
        if piece not in (
            "p", "n", "b", "r", "q", "k","P", "N", "B", "R", "Q", "K", "x"
        ):
            raise ValidationError(
                f"'{piece}' is not a valid piece code (nor 'x' to remove the piece)"
            ) 
        # fmt: on
        return square, piece


_INVALID_FEN_FALLBACK: "FEN" = "3k4/p7/8/8/8/8/7P/3K4 w - - 0 1"


def _get_game_presenter(
    fen: "FEN | None",
    bot_first_move: str | None,
    intro_turn_speech_square: "Square | None",
    game_update: GameUpdate | None,
) -> DailyChallengeGamePresenter:
    if not fen:
        fen = _INVALID_FEN_FALLBACK
    elif game_update:
        square, piece = game_update
        chess_board = chess.Board(fen)
        square_int = chess.parse_square(square)
        if piece == "x":
            chess_board.remove_piece_at(square_int)
        else:
            chess_board.set_piece_at(square_int, chess.Piece.from_symbol(piece))
        fen = cast("FEN", chess_board.fen())

    game_teams, piece_role_by_square = set_daily_challenge_teams_and_pieces_roles(
        fen=fen
    )
    challenge_preview = DailyChallenge(
        fen=fen,
        teams=game_teams,
        piece_role_by_square=piece_role_by_square,
    )

    game_state = PlayerGameState(
        attempts_counter=0,
        turns_counter=0,
        current_attempt_turns_counter=0,
        fen=fen,
        piece_role_by_square=piece_role_by_square,
        moves=bot_first_move or "",
    )

    return DailyChallengeGamePresenter(
        challenge=challenge_preview,
        game_state=game_state,
        refresh_last_move=True,
        is_htmx_request=False,
        forced_speech_bubble=(intro_turn_speech_square, "!")
        if intro_turn_speech_square
        else None,
        force_square_info=True,  # easier will all the square names :-)
    )

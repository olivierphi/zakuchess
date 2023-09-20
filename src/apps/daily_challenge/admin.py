import re
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Callable, Literal, TypeAlias, TypedDict, cast

import chess
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views.decorators.clickjacking import xframe_options_exempt

from ..chess.business_logic import calculate_fen_before_move
from .business_logic import set_daily_challenge_teams_and_pieces_roles
from .cookie_helpers import clear_daily_challenge_state_in_session
from .models import DailyChallenge
from .presenters import DailyChallengeGamePresenter

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.chess.types import FEN, PieceSymbol, Square

GameUpdateCommandParams: TypeAlias = dict[str, Any]
GameUpdateCommandType = Literal["add", "move", "remove"]
GameUpdateCommand: TypeAlias = tuple[GameUpdateCommandType, GameUpdateCommandParams]

_GAME_UPDATE_COMMAND_PATTERNS: dict[GameUpdateCommandType, re.Pattern] = {
    "add": re.compile(r"(?P<target>[a-hA-H][1-8]):add:(?P<piece>[pnbrqkPNBRQK])!"),
    "move": re.compile(r"(?P<from_>[a-hA-H][1-8]):mv:(?P<to>[a-hA-H][1-8])!"),
    "remove": re.compile(r"(?P<target>[a-hA-H][1-8]):rm!"),
}

_FUTURE_DAILY_CHALLENGE_COOKIE_DURATION = timedelta(minutes=20)

_INVALID_FEN_FALLBACK: "FEN" = "3k4/p7/8/8/8/8/7P/3K4 w - - 0 1"


class DailyChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = DailyChallenge
        fields = ("lookup_key", "fen", "bot_first_move", "intro_turn_speech_square")

    def clean_bot_first_move(self) -> str:
        return self.cleaned_data["bot_first_move"].lower()


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    form = DailyChallengeAdminForm

    list_display = ("lookup_key", "fen", "bot_first_move")
    readonly_fields = (
        "game_update",
        "game_preview",
        "fen_before_bot_first_move",
        "teams",
    )

    class Media:
        js = ("daily_challenge/admin_game_preview.js",)

    def view_on_site(self, obj: DailyChallenge):
        url = reverse(
            "admin:daily_challenge_play_future_challenge",
            kwargs={"lookup_key": obj.lookup_key},
        )
        return url

    def get_urls(self) -> list:
        urls = super().get_urls()
        my_urls = [
            path(
                "play-future-challenge/<str:lookup_key>/",
                self.admin_site.admin_view(self.play_future_daily_challenge_view),
                name="daily_challenge_play_future_challenge",
            ),
            path(
                "game-preview/",
                self.admin_site.admin_view(self.preview_daily_challenge_view),
                name="daily_challenge_game_preview",
            ),
        ]
        return my_urls + urls

    def play_future_daily_challenge_view(
        self, request: "HttpRequest", lookup_key: str
    ) -> HttpResponse:
        clear_daily_challenge_state_in_session(request=request)

        response = redirect("daily_challenge:daily_game_view")
        response.set_signed_cookie(
            "admin_daily_challenge_lookup_key",
            lookup_key,
            expires=now() + _FUTURE_DAILY_CHALLENGE_COOKIE_DURATION,
            httponly=True,
        )

        return response

    @method_decorator(xframe_options_exempt)
    def preview_daily_challenge_view(self, request: "HttpRequest") -> HttpResponse:
        from dominate.util import raw

        from apps.chess.components.chess_board import chess_arena
        from apps.webui.components.layout import page

        errors: dict = {}

        form = DailyChallengePreviewForm(request.GET)
        if not form.is_valid():
            errors = form.errors

        game_update_cmd = form.cleaned_data.get("game_update")
        game_presenter = _get_game_presenter(
            fen=form.cleaned_data.get("fen"),
            bot_first_move=form.cleaned_data.get("bot_first_move"),
            intro_turn_speech_square=form.cleaned_data.get("intro_turn_speech_square"),
            game_update_cmd=game_update_cmd,
        )

        return HttpResponse(
            page(
                # Hide the Zakuchess chrome:
                raw("<style>header, footer { display: none; }</style>"),
                # Display errors, if any:
                raw(
                    """<pre style="white-space: pre-wrap; background-color: #0f172a; color: #f1f5f9;">"""
                    "Errors:\n"
                    f"{errors!r}"
                    "</pre>"
                )
                if errors
                else "",
                # Display the score advantage:
                raw(
                    """<div style="background-color: #0f172a; color: #f1f5f9; text-align: center;">"""
                    f"Score advantage: <b>{game_presenter.naive_score}</b></div>"
                )
                if not errors
                else "",
                # Update the parent form with the new FEN:
                raw(
                    f"""<script>window.parent.document.getElementById("id_fen").value = "{game_presenter.fen}";</script>"""
                )
                if game_update_cmd
                else "",
                # Last but certainly not least, display the chess board:
                chess_arena(
                    game_presenter=game_presenter, status_bars=[], board_id="admin"
                ),
                request=request,
            )
        )

    @admin.display(description="Game update")
    def game_update(self, instance: DailyChallenge) -> str:
        return mark_safe(
            """
            <input type="text" class="vTextField" maxlength="10" id="id_update_game">
            <div class="help" id="id_update_game_helptext" style="margin-left: 0;">
                Available chess boards update commands:
                <ul>
                    <li><code>[square]:rm!</code>: removes the piece from a square - e.g. `e4:rm!`</li>
                    <li><code>[square]:add:[piece]!</code>: adds a piece to a square - e.g. `e4:add:p!`, `f6:add:N!`</li>
                    <li><code>[square_from]:mv:[square_to]!</code>: moves a piece- e.g. `e4:mv:e5!`, `f6:mv:f8!`</li>
                </ul>
                Any other string will be removed as soon as an exclamation mark is typed.
            </div>
            """
        )

    @admin.display(description="Game preview")
    def game_preview(self, instance: DailyChallenge) -> str:
        # Quick and (very) dirty management of the game preview
        return mark_safe(
            """
            <div id="admin-preview-url-holder" style="display: none;">${ADMIN_PREVIEW_URL}</div>
            
            <iframe
                id="preview-iframe"
                style="width: 400px; aspect-ratio: 1 / 1.3; border: solid white 1px; border-radius: 3px;">
            </iframe>
            
            <div style="margin: 1rem 0;">
                Can always help: <a href="https://www.dailychess.com/chess/chess-fen-viewer.php" 
                    rel="noreferrer noopener" >www.dailychess.com/chess/chess-fen-viewer.php</a>
            </div>
            
            """.replace(
                "${ADMIN_PREVIEW_URL}", reverse("admin:daily_challenge_game_preview")
            )
        )


def _get_game_presenter(
    fen: "FEN | None",
    bot_first_move: str | None,
    intro_turn_speech_square: "Square | None",
    game_update_cmd: GameUpdateCommand | None,
) -> DailyChallengeGamePresenter:
    from .types import PlayerGameState

    if not fen:
        fen = _INVALID_FEN_FALLBACK
    elif game_update_cmd:
        fen = _apply_game_update(fen=fen, game_update_cmd=game_update_cmd)

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


def _apply_game_update(*, fen: "FEN", game_update_cmd: GameUpdateCommand) -> "FEN":
    """Dispatches the game update command to the appropriate function."""
    cmd_type, params = game_update_cmd
    return _GAME_UPDATE_MAPPING[cmd_type](fen=fen, **params)


def _add_piece_to_square(*, fen: "FEN", target: "Square", piece: "PieceSymbol") -> str:
    chess_board = chess.Board(fen)
    square_int = chess.parse_square(target.lower())
    chess_board.set_piece_at(square_int, chess.Piece.from_symbol(piece))
    return cast("FEN", chess_board.fen())


def _move_piece_to_square(*, fen: "FEN", from_: "Square", to: "Square") -> str:
    chess_board = chess.Board(fen)
    square_from_int = chess.parse_square(from_.lower())
    square_to_int = chess.parse_square(to.lower())
    piece = chess_board.piece_at(square_from_int)
    chess_board.remove_piece_at(square_from_int)
    chess_board.set_piece_at(square_to_int, piece)
    return cast("FEN", chess_board.fen())


def _remove_piece_from_square(*, fen: "FEN", target: "Square") -> str:
    chess_board = chess.Board(fen)
    square_int = chess.parse_square(target.lower())
    chess_board.remove_piece_at(square_int)
    return cast("FEN", chess_board.fen())


_GAME_UPDATE_MAPPING: dict[GameUpdateCommandType, Callable] = {
    "add": _add_piece_to_square,
    "move": _move_piece_to_square,
    "remove": _remove_piece_from_square,
}


class DailyChallengePreviewForm(forms.Form):
    fen = forms.CharField(min_length=20, max_length=90)
    bot_first_move = forms.CharField(max_length=4, required=False)
    intro_turn_speech_square = forms.CharField(max_length=2, required=False)
    game_update = forms.CharField(min_length=4, max_length=10, required=False)

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
        if not bot_first_move or len(bot_first_move) != 4:
            return None
        fen = self.cleaned_data.get("fen", "")
        if not fen:
            return None
        try:
            calculate_fen_before_move(
                fen_after_move=fen,
                move_uci=bot_first_move,  # type: ignore
                moving_player_side="b",
            )
        except ValueError as exc:
            raise ValidationError(exc) from exc
        return bot_first_move

    def clean_intro_turn_speech_square(self) -> "Square | None":
        intro_turn_speech_square = self.cleaned_data.get("intro_turn_speech_square", "")
        if not intro_turn_speech_square or len(intro_turn_speech_square) != 2:
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

    def clean_game_update(self) -> GameUpdateCommand | None:
        game_update = self.cleaned_data.get("game_update")
        if not game_update:
            return None
        for cmd_type, pattern in _GAME_UPDATE_COMMAND_PATTERNS.items():
            if match := pattern.match(game_update):
                return cmd_type, match.groupdict()

        raise ValidationError(f"'{game_update}' is not a valid game update command")

    if TYPE_CHECKING:

        class CleanedData(TypedDict):
            fen: "FEN"
            bot_first_move: str | None
            intro_turn_speech_square: "Square | None"
            game_update: GameUpdateCommand

        cleaned_data: CleanedData

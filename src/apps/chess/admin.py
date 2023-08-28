from typing import TYPE_CHECKING

import chess
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .domain.mutations import create_new_daily_challenge
from .domain.queries import calculate_fen_before_bot_first_move
from .models import DailyChallenge

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .domain.types import PlayerSide

BOT_SIDE: "PlayerSide" = "b"


class DailyChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = DailyChallenge
        fields = ("id", "fen", "bot_first_move")

    def clean_bot_first_move(self) -> str:
        """Will generated the "fen_before_bot_first_move" field."""
        bot_first_move = self.cleaned_data["bot_first_move"].lower()

        chess_board = chess.Board(self.cleaned_data["fen"])
        try:
            fen_before_bot_first_move = calculate_fen_before_bot_first_move(
                chess_board=chess_board, bot_first_move=bot_first_move, bot_side=BOT_SIDE
            )
        except ValueError as exc:
            raise ValidationError(exc.args[0]) from exc

        self.cleaned_data["fen_before_bot_first_move"] = fen_before_bot_first_move

        return bot_first_move

    # def clean_name(self):


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    form = DailyChallengeAdminForm

    def save_model(
        self, request: "HttpRequest", obj: DailyChallenge, form: DailyChallengeAdminForm, change: bool
    ) -> None:
        cleaned_data = form.cleaned_data
        try:
            obj = create_new_daily_challenge(
                id_=cleaned_data["id"],
                fen=cleaned_data["fen"],
                bot_first_move=cleaned_data["bot_first_move"],
                fen_before_bot_first_move=cleaned_data["fen_before_bot_first_move"],
                save=False,
            )
        except ValueError as exc:
            raise ValidationError(exc.args[0]) from exc

        super().save_model(request, obj, form, change)

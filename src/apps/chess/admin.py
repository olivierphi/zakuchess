from typing import TYPE_CHECKING

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .business_logic import create_new_daily_challenge
from .models import DailyChallenge

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .business_logic.types import PlayerSide

BOT_SIDE: "PlayerSide" = "b"


class DailyChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = DailyChallenge
        fields = ("id", "fen", "bot_first_move")

    def clean_bot_first_move(self) -> str:
        return self.cleaned_data["bot_first_move"].lower()


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
            )
        except ValueError as exc:
            raise ValidationError(exc.args[0]) from exc

        super().save_model(request, obj, form, change)

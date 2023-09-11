from django import forms
from django.contrib import admin

from .models import DailyChallenge


class DailyChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = DailyChallenge
        fields = ("id", "fen", "bot_first_move", "intro_turn_speech_square")

    def clean_bot_first_move(self) -> str:
        return self.cleaned_data["bot_first_move"].lower()


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    form = DailyChallengeAdminForm

    list_display = ("id", "fen", "bot_first_move", "fen_before_bot_first_move", "teams")

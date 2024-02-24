from django import forms

from apps.chess.models import UserPrefs, UserPrefsGameSpeed, UserPrefsGameSpeedChoices


class UserPrefsForm(forms.Form):
    game_speed = forms.TypedChoiceField(
        choices=UserPrefsGameSpeedChoices,
        coerce=int,
    )

    def to_user_prefs(self) -> UserPrefs | None:
        if not self.is_valid():
            return None

        return UserPrefs(
            game_speed=UserPrefsGameSpeed(self.cleaned_data["game_speed"]),
        )

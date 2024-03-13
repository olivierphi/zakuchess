from django import forms

from apps.chess.models import (
    UserPrefs,
    UserPrefsBoardTexture,
    UserPrefsBoardTextureChoices,
    UserPrefsGameSpeed,
    UserPrefsGameSpeedChoices,
)


class UserPrefsForm(forms.Form):
    game_speed = forms.TypedChoiceField(
        choices=UserPrefsGameSpeedChoices,
        coerce=int,
    )
    board_texture = forms.TypedChoiceField(
        choices=UserPrefsBoardTextureChoices,
        coerce=int,
    )

    def to_user_prefs(self) -> UserPrefs | None:
        if not self.is_valid():
            return None

        return UserPrefs(
            game_speed=UserPrefsGameSpeed(self.cleaned_data["game_speed"]),
            board_texture=UserPrefsBoardTexture(self.cleaned_data["board_texture"]),
        )

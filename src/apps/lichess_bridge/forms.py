from django import forms

from .models import LichessCorrespondenceGameDaysChoice


class LichessCorrespondenceGameCreationForm(forms.Form):
    days_per_turn = forms.ChoiceField(
        choices=LichessCorrespondenceGameDaysChoice.choices
    )

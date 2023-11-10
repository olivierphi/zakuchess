from typing import TYPE_CHECKING, TypedDict

from django import forms

from apps.chess.consts import MOVES, SQUARES

if TYPE_CHECKING:
    from apps.chess.types import Move, Square

_SQUARE_CHOICES = [(square, square) for square in SQUARES]
_MOVE_CHOICES = [(move, move) for move in MOVES]


def SquareField(**kwargs) -> forms.ChoiceField:
    # a bit hackish, but it does the job ^_^  (should rather be a proper FormField
    # class, or a function that doesn't pretend to be a class by its naming)
    return forms.ChoiceField(choices=_SQUARE_CHOICES, **kwargs)


def MoveField(**kwargs) -> forms.ChoiceField:
    # ditto
    return forms.ChoiceField(choices=_MOVE_CHOICES, **kwargs)


class HtmxGameSelectPieceForm(forms.Form):
    square = SquareField()

    if TYPE_CHECKING:

        class CleanedData(TypedDict):
            square: "Square"

        @property
        def cleaned_data(self) -> "CleanedData":
            raise NotImplementedError  # just for type-checking


class HtmxGameMovePieceForm(forms.Form):
    from_ = SquareField()
    to = SquareField()

    if TYPE_CHECKING:

        class CleanedData(TypedDict):
            from_: "Square"
            to: "Square"

        @property
        def cleaned_data(self) -> "CleanedData":
            raise NotImplementedError  # just for type-checking


class HtmxGamePlayBotMoveForm(forms.Form):
    move = MoveField()

    if TYPE_CHECKING:

        class CleanedData(TypedDict):
            move: "Move"

        @property
        def cleaned_data(self) -> "CleanedData":
            raise NotImplementedError  # just for type-checking

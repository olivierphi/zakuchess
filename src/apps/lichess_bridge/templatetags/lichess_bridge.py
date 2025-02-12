from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    pass


register = template.Library()


_NON_GAME_PAGE_MAIN_SECTION_BASE_CSS = (
    "w-full mx-auto py-4 bg-slate-900 text-slate-50 min-h-48 md:max-w-3xl"
)
_NON_GAME_PAGE_SECTION_INNER_CONTAINER_CSS = "px-8 pb-8 md:px-0 md:w-8/12 md:mx-auto"


_ONE_DAY = 86_400
_TWO_DAYS = _ONE_DAY * 2


@register.filter
def game_time_left_display(seconds_left: int) -> str:
    # TODO: i18n
    # TODO: write a test for this
    if seconds_left < 1:
        return "time's up"
    if seconds_left < 60:
        return f"{seconds_left} seconds"
    if seconds_left < 3600:
        return f"{round(seconds_left / 60)} minutes"
    if seconds_left < _ONE_DAY:
        return f"{round(seconds_left / 3600)} hours"
    if seconds_left < _TWO_DAYS:
        return f"1 day and {round((seconds_left - _ONE_DAY) / 3600)} hours"
    return f"{round(seconds_left / _ONE_DAY)} days"

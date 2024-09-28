from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import button, div, fieldset, form, input_, label, legend, p

from apps.lichess_bridge.components.svg_icons import ICON_SVG_CREATE
from apps.lichess_bridge.models import LichessCorrespondenceGameDaysChoice
from apps.webui.components import common_styles
from apps.webui.components.forms_common import csrf_hidden_input

if TYPE_CHECKING:
    from django.http import HttpRequest


def game_creation_form(*, request: "HttpRequest", form_errors: dict) -> form:
    return form(
        csrf_hidden_input(request),
        div(
            fieldset(
                legend("Days per move:", cls="font-bold"),
                (
                    p(form_errors["days_per_turn"], cls="text-red-600 ")
                    if "days_per_turn" in form_errors
                    else ""
                ),
                div(
                    *[
                        div(
                            input_(
                                id=f"days-per-turn-{value}",
                                type="radio",
                                name="days_per_turn",
                                value=value,
                                checked=(
                                    value
                                    == LichessCorrespondenceGameDaysChoice.THREE_DAYS.value  # type: ignore[attr-defined]
                                ),
                            ),
                            label(display, html_for=f"days-per-turn-{value}"),
                            cls="w-1/4 flex-none",
                        )
                        for value, display in LichessCorrespondenceGameDaysChoice.choices
                    ],
                    cls="flex flex-wrap",
                ),
                cls="block text-sm font-bold mb-2",
            ),
            cls="mb-8",
        ),
        div(
            button(
                "Create",
                " ",
                ICON_SVG_CREATE,
                type="submit",
                cls=common_styles.BUTTON_CLASSES,
            ),
            cls="text-center",
        ),
        action=reverse("lichess_bridge:create_game"),
        method="POST",
    )

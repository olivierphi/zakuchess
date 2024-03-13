from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import button, div, fieldset, form, h3, h4, input_, label, legend

from apps.chess.components.misc_ui import modal_container
from apps.chess.components.svg_icons import ICON_SVG_CONFIRM
from apps.chess.models import UserPrefsBoardTextureChoices, UserPrefsGameSpeedChoices

from .common_styles import BUTTON_CONFIRM_CLASSES
from .svg_icons import ICON_SVG_COG

if TYPE_CHECKING:
    from typing import Any

    from django.db.models import Choices
    from dominate.tags import dom_tag

    from apps.chess.models import UserPrefs


# TODO: manage i18n


def user_prefs_modal(*, user_prefs: "UserPrefs") -> "dom_tag":
    return modal_container(
        header=h3(
            "Preferences ",
            ICON_SVG_COG,
            cls="text-xl",
        ),
        body=div(
            # div("Select your preferences, and save them using the 'Save' button.", cls="mb-4"),
            _user_prefs_form(user_prefs),
            cls="p-6 space-y-6",
        ),
    )


def _user_prefs_form(user_prefs: "UserPrefs") -> "dom_tag":
    form_htmx_attributes = {
        "data_hx_post": reverse("daily_challenge:htmx_daily_challenge_user_prefs_save"),
        "data_hx_target": "#modals-container",
        "data_hx_swap": "innerHTML",
    }

    game_speed = _form_fieldset(
        fieldset_legend="Game speed",
        input_name="game_speed",
        choices=UserPrefsGameSpeedChoices,
        # We may revisit these icons-per-choice later, but let's comment this out
        # for the moment.
        ## choices_icons={
        ##     UserPrefsGameSpeedChoices.NORMAL: ICON_SVG_PLAY,
        ##     UserPrefsGameSpeedChoices.FAST: ICON_SVG_FORWARD,
        ## },
        current_value=user_prefs.game_speed,
    )

    board_texture = _form_fieldset(
        fieldset_legend="Chess board texture",
        input_name="board_texture",
        choices=UserPrefsBoardTextureChoices,
        current_value=user_prefs.board_texture,
    )

    submit_button = (
        button(
            "Save preferences",
            " ",
            ICON_SVG_CONFIRM,
            cls=BUTTON_CONFIRM_CLASSES,
        ),
    )

    return form(
        game_speed,
        board_texture,
        div(submit_button, cls="mt-8 mb-4 text-center"),
        **form_htmx_attributes,
    )


def _form_fieldset(
    *,
    fieldset_legend: str,
    input_name: str,
    choices: "type[Choices]",
    # choices_icons: dict,
    current_value: "Any",
) -> fieldset:
    return fieldset(
        legend(
            h4(fieldset_legend, cls="flex items-center font-bold"),
        ),
        div(
            *[
                label(
                    # span(
                    #     choices_icons[choice.value],
                    #     cls="mr-2 inline-flex p-px items-center bg-yellow-400 text-slate-900 rounded-full",
                    # ),
                    input_(
                        value=str(choice.value),
                        type="radio",
                        name=input_name,
                        id=f"{input_name}_input_{choice.name}",
                        cls="mr-2",
                        **({"checked": True} if choice.value == current_value else {}),
                    ),
                    choice.label,
                    cls="flex my-2 items-center hover:cursor-pointer",
                    _for=f"{input_name}_input_{choice.name}",
                )
                for choice in choices
            ]
        ),
        cls="mt-2",
    )

from functools import cache
from typing import TYPE_CHECKING

from django.conf import settings
from dominate.tags import div, h4, p, span
from dominate.util import raw

from apps.webui.components import common_styles
from apps.webui.components.chess_units import (
    CHARACTER_TYPE_TIP,
    chess_status_bar_tip,
    unit_display_container,
)
from apps.webui.components.misc_ui.svg_icons import ICON_SVG_COG

from .svg_icons import (
    ICON_SVG_LIGHT_BULB,
    ICON_SVG_RESTART,
)

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from apps.chess.models import GameFactions


@cache
def help_content(
    *,
    challenge_solution_turns_count: int,
    factions: "GameFactions",
) -> "dom_tag":
    spacing = "mb-3"

    return raw(
        div(
            h4(
                "Welcome to this new daily challenge!",
                cls=f"{spacing} text-yellow-400 font-bold ",
            ),
            div(
                p(
                    raw(
                        "Today's challenge "
                        f"<b>can be solved in {challenge_solution_turns_count} turns</b>."
                    )
                ),
                cls=f"{spacing}",
            ),
            div(
                "Your pieces are the ones with a green circle, like these:",
                div(
                    unit_display_container(piece_role="N1", factions=factions),
                    unit_display_container(piece_role="Q", factions=factions),
                    cls="w-full flex justify-center gap-3",
                ),
                "Tap one of them to start playing.",
                cls=f"{spacing}",
            ),
            div(
                raw("You can <b>restart from the beginning</b> at any time, "),
                "by clicking the ",
                span(
                    "Retry",
                    ICON_SVG_RESTART,
                    cls=f"{common_styles.BUTTON_CLASSES.replace(common_styles.BUTTON_BASE_HOVER_TEXT_COLOR, '')} !mx-0",
                ),
                " button.",
                cls=f"{spacing}",
            ),
            div(
                "If you can't solve today's challenge ",
                raw("you can decide to <b>see a solution</b>, by clicking the "),
                span(
                    "See solution",
                    ICON_SVG_LIGHT_BULB,
                    cls=f"{common_styles.BUTTON_CLASSES} !inline-block !mx-0",
                ),
                " button.",
                cls=f"{spacing}",
            ),
            div(
                raw("You can <b>customise some game settings</b>"),
                " - such as the speed of the game or the appearance of the board - via the ",
                span(
                    "Options",
                    ICON_SVG_COG,
                    cls=f"{common_styles.BUTTON_CLASSES} !inline-block !mx-0",
                ),
                " button.",
                cls=f"{spacing}",
            ),
            div("Good luck! 🙂", cls=f"p-3 {spacing} font-bold"),
            div(
                div(
                    span("🛡 Your troops", cls="text-yellow-400 font-bold"),
                    span(""),
                    span("The undead 💀", cls="text-yellow-400 font-bold"),
                    cls="flex w-full justify-between items-center",
                ),
                *(
                    chess_status_bar_tip(
                        factions=factions,
                        piece_type=piece_type,
                        additional_classes="h-20",
                        row_counter=i,
                    )
                    for i, piece_type in enumerate(CHARACTER_TYPE_TIP.keys())
                ),
                cls="mt-2",
            ),
            cls="w-full text-center",
        ).render(pretty=settings.DEBUG)
    )

from math import ceil, floor
from typing import TYPE_CHECKING

from dominate.tags import button, div, h3, i, span

from ...consts import MAXIMUM_TURNS_PER_CHALLENGE
from .svg_icons import ICON_SVG_CLOSE, ICON_SVG_STATS

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from ...types import PlayerStats

# TODO: manage i18n


def stats_modal(stats: "PlayerStats") -> "dom_tag":
    # Converted from https://flowbite.com/docs/components/modal/

    modal_header = div(
        h3(
            "Statistics ",
            ICON_SVG_STATS,
            cls="text-xl",
        ),
        button(
            ICON_SVG_CLOSE,
            span("Close modal", cls="sr-only"),
            type="button",
            onclick="closeModal()",
        ),
        cls="flex items-start justify-between p-4 border-b rounded-t",
    )

    modal_body = div(
        _main_stats(stats),
        _wins_distribution(stats),
        cls="p-6 space-y-6",
    )

    modal_footer = div(
        i("One Zakuchess a day keeps the doctor away."),
        cls="text-sm text-center p-6 space-x-2 border-t border-gray-200 rounded-b",
    )

    modal_content = div(
        modal_header,
        modal_body,
        modal_footer,
        cls="relative mt-8 bg-gray-950 rounded-lg shadow shadow-slate-950",
    )

    return div(
        div(
            modal_content,
            cls="relative w-full mx-auto max-w-2xl max-h-full",
        ),
        cls=" ".join(
            (
                "fixed top-0 left-0 right-0 z-50 w-full overflow-x-hidden overflow-y-auto",
                "md:inset-0 h-[calc(100%-1rem)] max-h-full",
                "bg-gray-900/75 p-1 text-slate-100 ",
            )
        ),
        id="modals-container",
    )


def _main_stats(stats: "PlayerStats") -> "dom_tag":
    def stat(name: str, value: int) -> "dom_tag":
        return div(
            div(str(value), cls="font-bold text-lg text-center"),
            div(name, cls="text-sm text-center"),
        )

    return div(
        stat("Played", stats.games_count),
        stat("Win %", stats.win_rate),
        stat("Current streak", stats.current_streak),
        stat("Max streak", stats.max_streak),
        cls="flex justify-between",
    )


def _wins_distribution(stats: "PlayerStats") -> "dom_tag":
    max_value: int = max(stats.wins_distribution.values())

    if max_value == 0:
        content: "dom_tag" = div(
            "No win yet",
            cls="text-center",
        )
    else:
        slices_size = MAXIMUM_TURNS_PER_CHALLENGE / stats.WINS_DISTRIBUTION_SLICE_COUNT
        min_width_percentage = 8

        def row(distribution_slice: int, count: int) -> "dom_tag":
            slice_lower_bound = floor(slices_size * (distribution_slice - 1)) + 1
            slice_upper_bound = floor(slice_lower_bound + slices_size) - 1

            return div(
                div(
                    f"{slice_lower_bound} - {slice_upper_bound} turns",
                    cls="font-bold",
                ),
                div(
                    str(count),
                    cls="bg-lime-800 font-bold text-right px-2",
                    # Cannot use Tailwind for this, as it's totally dynamic - let's just
                    # fall back to good old inline styles ^_^
                    style=f"width: {max(ceil(count/max_value*100), min_width_percentage)}%"
                    if count > 0
                    else "display: inline-block",
                ),
                cls="mb-1",
            )

        content = div(
            *[row(k, v) for k, v in stats.wins_distribution.items()],
            cls="",
        )

    return div(
        div("Wins distribution", cls="font-bold text-center mb-2"),
        content,
        cls="min-h-24",
    )

from math import ceil, floor
from typing import TYPE_CHECKING

from dominate.tags import div, h3

from apps.chess.components.misc_ui import modal_container

from .svg_icons import ICON_SVG_STATS

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from ...models import PlayerStats

# TODO: manage i18n


def stats_modal(stats: "PlayerStats") -> "dom_tag":
    return modal_container(
        header=h3(
            "Statistics ",
            ICON_SVG_STATS,
            cls="text-xl",
        ),
        body=div(
            _main_stats(stats),
            _wins_distribution(stats),
            cls="p-6 space-y-6",
        ),
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
            "No victories yet",
            cls="text-center",
        )
    else:
        slices_size = stats.WINS_DISTRIBUTION_SLICE_SIZE
        min_width_percentage = 8

        def row(distribution_slice: int, count: int) -> "dom_tag":
            slice_lower_bound = floor(slices_size * (distribution_slice - 1)) + 1
            slice_upper_bound = floor(slice_lower_bound + slices_size) - 1
            slice_label = (
                f"{slice_upper_bound} turns or less"
                if distribution_slice < stats.WINS_DISTRIBUTION_SLICE_COUNT
                else f"More than {slice_lower_bound - 1} turns "
            )

            return div(
                div(
                    slice_label,
                    cls="font-bold",
                ),
                div(
                    str(count),
                    cls="bg-lime-800 font-bold text-right px-2",
                    # Cannot use Tailwind for this, as it's totally dynamic - let's just
                    # fall back to good old inline styles ^_^
                    style=(
                        f"width: {max(ceil(count/max_value*100), min_width_percentage)}%"
                        if count > 0
                        else "display: inline-block"
                    ),
                ),
                cls="mb-1",
            )

        content = div(
            *[row(k, v) for k, v in stats.wins_distribution.items()],
            cls="",
        )

    return div(
        div("Victories distribution", cls="font-bold text-center mb-2"),
        content,
        cls="min-h-24",
    )

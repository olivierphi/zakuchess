from math import ceil
from typing import TYPE_CHECKING

from django.contrib.humanize.templatetags.humanize import ordinal
from dominate.tags import div, h3, p
from dominate.util import raw

from apps.chess.components.misc_ui import modal_container

from ...business_logic import has_player_won_today
from .svg_icons import ICON_SVG_STATS

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from ...models import (
        DailyChallenge,
        PlayerGameState,
        PlayerStats,
        WinsDistributionSlice,
    )

# TODO: manage i18n


def stats_modal(
    *, stats: "PlayerStats", game_state: "PlayerGameState", challenge: "DailyChallenge"
) -> "dom_tag":
    return modal_container(
        header=h3(
            "Statistics ",
            ICON_SVG_STATS,
            cls="text-xl",
        ),
        body=div(
            _main_stats(stats),
            _today_s_results(stats=stats, game_state=game_state, challenge=challenge),
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


def _today_s_results(
    *, stats: "PlayerStats", game_state: "PlayerGameState", challenge: "DailyChallenge"
) -> "dom_tag":
    if not has_player_won_today(stats):
        return div()  # empty <div>

    # We repeat the logic we have in "status_bar.py". If we have to copy it once more
    # we'll factorise it.
    total_turns_counter = game_state.turns_counter + 1
    turns_counter = game_state.victory_turns_count
    attempts_counter = game_state.attempts_counter + 1
    our_solution_turns_count = challenge.solution_turns_count

    return div(
        p(
            raw(
                f"Today you won in <b>{attempts_counter} "
                f"attempt{'s' if attempts_counter > 1 else ''}</b>. 🎉"
            ),
        ),
        p(
            raw(f"The battled lasted for <b>{turns_counter} turns</b>."),
        ),
        p(
            raw(
                f"(our scouts' solution needed {our_solution_turns_count} turns)",
            ),
        ),
        (
            p(
                raw(
                    f"Across all your attempts you played <b>{total_turns_counter} turns today</b>."
                )
            )
            if attempts_counter > 1
            else ""
        ),
        cls="text-sm text-center",
    )


def _wins_distribution(stats: "PlayerStats") -> "dom_tag":
    max_value: int = max(stats.wins_distribution.values())

    if max_value == 0:
        content: "dom_tag" = div(
            "No victories yet",
            cls="text-center",
        )
    else:
        min_width_percentage = 8

        def row(distribution_slice: "WinsDistributionSlice", count: int) -> "dom_tag":
            slice_label = (
                f"{ordinal(distribution_slice)} attempt"
                if distribution_slice < stats.WINS_DISTRIBUTION_SLICE_COUNT
                else f"{stats.WINS_DISTRIBUTION_SLICE_COUNT} attempts or more"
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

from typing import TYPE_CHECKING

from dominate.tags import button, div, dom_tag, h3, span

from .svg_icons import ICON_SVG_CLOSE, ICON_SVG_STATS

if TYPE_CHECKING:
    from ...types import PlayerStats


def stats_modal(stats: "PlayerStats") -> dom_tag:
    # Converted from https://flowbite.com/docs/components/modal/

    modal_header = div(
        h3(
            "Statistics",
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
        # TODO: implement this
        "[wins count bucketed by number of turns it took to win]",
        cls="p-6 space-y-6 min-h-40",
    )

    modal_footer = div(
        "[footer]",
        cls="flex items-center text-center p-6 space-x-2 border-t border-gray-200 rounded-b",
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
                "bg-slate-900/75 p-1 text-slate-100 ",
            )
        ),
        id="modals-container",
    )


def _main_stats(stats: "PlayerStats") -> dom_tag:
    def stat(name: str, value: int) -> dom_tag:
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

from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import a, b, caption, div, table, tbody, td, th, thead, tr

from apps.chess.chess_helpers import get_turns_counter_from_fen

from .game_info import time_left_display

if TYPE_CHECKING:
    from dominate.tags import html_tag

    from ..models import LichessOngoingGameData


def lichess_ongoing_games(ongoing_games: "list[LichessOngoingGameData]") -> "html_tag":
    th_classes = "p-2"

    return div(
        table(
            caption("Correspondence games", cls="mb-2 text-slate-50 "),
            thead(
                tr(
                    th("Opponent", cls=th_classes),
                    th("Moves", cls=th_classes),
                    th("Time", cls=th_classes),
                    th("Turn", cls=th_classes),
                    cls="bg-rose-900 text-slate-200 font-bold",
                ),
            ),
            tbody(
                *[_ongoing_game_row(game) for game in ongoing_games]
                if ongoing_games
                else tr(
                    td(
                        div(
                            "You have no ongoing games on Lichess at the moment",
                            cls="italic p-8 text-center",
                        ),
                        colspan=4,
                    )
                ),
            ),
            cls="w-full border-separate border-spacing-0 border border-slate-500 rounded-md",
        ),
        cls="my-4 px-1 ",
    )


def _ongoing_game_row(game: "LichessOngoingGameData") -> tr:
    td_classes = "border border-slate-300 dark:border-slate-700 p-1 text-slate-500 dark:text-slate-400"
    return tr(
        td(
            a(
                game.opponent.username,
                href=reverse(
                    "lichess_bridge:correspondence_game",
                    kwargs={"game_id": game.gameId},
                ),
                cls="font-bold underline",
            ),
            cls=td_classes,
        ),
        td(get_turns_counter_from_fen(game.fen), cls=f"{td_classes} text-right"),
        td(time_left_display(game.secondsLeft), cls=f"{td_classes} text-right"),
        td(b("Mine") if game.isMyTurn else "Theirs", cls=f"{td_classes} text-right"),
    )

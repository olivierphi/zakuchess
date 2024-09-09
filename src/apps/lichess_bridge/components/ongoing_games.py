from typing import TYPE_CHECKING

from django.urls import reverse
from dominate.tags import a, caption, div, table, tbody, td, th, thead, tr

from ...chess.chess_helpers import get_turns_counter_from_fen
from .misc_ui import time_left_display

if TYPE_CHECKING:
    from dominate.tags import html_tag

    from ..models import LichessOngoingGameData


def lichess_ongoing_games(ongoing_games: "list[LichessOngoingGameData]") -> "html_tag":
    th_classes = "border border-slate-300 dark:border-slate-600 font-semibold p-2 text-slate-900 dark:text-slate-200"

    return table(
        caption("Your ongoing games", cls="mb-2"),
        thead(
            tr(
                th("Opponent", cls=th_classes),
                th("Moves", cls=th_classes),
                th("Time", cls=th_classes),
                th("Turn", cls=th_classes),
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
        cls="w-full my-4 border-separate border-spacing-2 border border-slate-500 rounded-md",
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
            ),
            cls=td_classes,
        ),
        td(get_turns_counter_from_fen(game.fen), cls=td_classes),
        td(time_left_display(game.secondsLeft), cls=td_classes),
        td("Mine" if game.isMyTurn else "Theirs", cls=td_classes),
    )

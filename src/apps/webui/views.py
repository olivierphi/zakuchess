from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import render

from apps.chess.game_state import GameState

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def home_page(request: HttpRequest) -> HttpResponse:
    game_state = GameState(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        board_orientation="8-to-1",
        # board_orientation="1-to-8",
    )
    return render(request, "webui/home_page.html", {"game_state": game_state})

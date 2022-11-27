from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def hello_chess_board(req: HttpRequest) -> HttpResponse:
    return render(req, "chess/chessboard.tpl.html")

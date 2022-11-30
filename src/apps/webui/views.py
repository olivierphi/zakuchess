from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.chess.domain.mutations import create_new_game, game_move_piece, update_game_model
from apps.chess.domain.queries import get_chess_board_state, get_piece_available_targets
from apps.chess.domain.types import SquareName
from apps.chess.models import Game

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def hello_chess_board(req: HttpRequest) -> HttpResponse:
    game = create_new_game(save=False)
    return render(req, "webui/layout.tpl.html", {"game": game, "board_state": get_chess_board_state()})
    # return render(req, "chess/chessboard.tpl.html")


def game_new(req: HttpRequest) -> HttpResponse:
    new_game = create_new_game(is_versus_bot=True)
    return redirect(f"/games/{new_game.id}")


def game_view(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    board_state = game.get_board_state()

    return render(req, "webui/layout.tpl.html", {"game": game, "board_state": board_state})


def htmx_game_select_piece(req: HttpRequest, game_id: str, piece_square: SquareName) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    chess_board = game.get_chess_board()
    piece_available_targets = get_piece_available_targets(chess_board=chess_board, piece_square=piece_square)

    board_state = game.get_board_state().replace(selected_piece_square=piece_square)

    return render(
        req,
        "webui/htmx_partials/board_piece_available_targets.tpl.html",
        {
            "game": game,
            "board_state": board_state,
            "piece_available_targets": piece_available_targets,
        },
    )


@require_POST
def htmx_game_move_piece(
    req: HttpRequest, game_id: str, from_square: SquareName, to_square: SquareName
) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    board_state = game.get_board_state()
    result = game_move_piece(board_state=board_state, from_square=from_square, to_square=to_square)

    update_game_model(game=game, board_state=result.board_state)

    return render(
        req,
        "webui/htmx_partials/board_piece_moved.tpl.html",
        {
            "game": game,
            "board_state": result.board_state,
        },
    )

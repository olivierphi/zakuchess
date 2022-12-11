from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_safe
from apps.chess.domain.helpers import get_squares_with_pieces_that_can_move

from apps.chess.domain.mutations import create_new_game, game_move_piece, update_game_model
from apps.chess.domain.queries import get_chess_board_state, get_piece_available_targets
from apps.chess.domain.types import Square
from apps.chess.models import Game

if TYPE_CHECKING:
    from django.http import HttpRequest


@require_safe
def hello_chess_board(req: HttpRequest) -> HttpResponse:
    return redirect(f"/games/new/")


def game_new(req: HttpRequest) -> HttpResponse:
    new_game = create_new_game(bot_side="b")
    return redirect(f"/games/{new_game.id}")


@require_safe
def game_view(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    chess_board = game.get_chess_board()
    board_state = game.get_board_state()
    squares_with_pieces_that_can_move = get_squares_with_pieces_that_can_move(chess_board)

    return render(req, "webui/layout.tpl.html", {"game": game, "board_state": board_state, "squares_with_pieces_that_can_move": squares_with_pieces_that_can_move,})


def htmx_game_select_piece(req: HttpRequest, game_id: str, piece_square: Square) -> HttpResponse:
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
def htmx_game_move_piece(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    chess_board = game.get_chess_board()
    board_state = game.get_board_state()

    from_ = cast(Square, req.POST.get("from"))
    to = cast(Square, req.POST.get("to"))
    result = game_move_piece(board_state=board_state, from_square=from_, to_square=to)

    update_game_model(game=game, board_state=result.board_state)

    # Let's inform the next player of their legal moves:
    squares_with_pieces_that_can_move = get_squares_with_pieces_that_can_move(result.board)

    return render(
        req,
        "webui/htmx_partials/board_piece_moved.tpl.html",
        {
            "game": game,
            "board_state": result.board_state,
            "squares_with_pieces_that_can_move": squares_with_pieces_that_can_move,
        },
    )

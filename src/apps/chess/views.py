from __future__ import annotations

from typing import TYPE_CHECKING, cast
from zlib import adler32

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag, require_POST, require_safe

from apps.chess.domain.mutations import create_new_game, game_move_piece
from apps.chess.domain.queries._get_bot_next_move import get_bot_next_move
from apps.chess.domain.types import Square
from apps.chess.models import Game
from apps.chess.presenters import GamePresenter

if TYPE_CHECKING:
    from django.http import HttpRequest


def _game_etag(req: HttpRequest, game_id: str) -> str:
    hash_data = (
        game_id,
        req.path,
        # TODO: add the authenticated user's ID to the hash
        str(int(Game.objects.filter(id=game_id).values_list("updated_at", flat=True).get().timestamp())),
    )
    return str(adler32("::".join(hash_data).encode("utf-8")))


@require_safe
def hello_chess_board(req: HttpRequest) -> HttpResponse:
    return redirect("/games/new/")


def game_new(req: HttpRequest) -> HttpResponse:
    new_game = create_new_game(bot_side="b")
    return redirect(f"/games/{new_game.id}")


@require_safe
@cache_control(private=True)
@etag(_game_etag)
def game_view(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
    )

    return render(
        req,
        "chess/chess-game.tpl.html",
        {
            "game_presenter": game_presenter,
        },
    )


@require_safe
@cache_control(private=True)
@etag(_game_etag)
def htmx_game_no_selection(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    # TODO: validate this data
    board_id = cast(str, req.GET.get("board_id"))

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
    )

    return render(
        req,
        # No pieces were actually moved here, but as this template renders the whole pieces and
        # an empty targets container we can just re-use it to display a "waiting_for_player_selection" board:
        "chess/htmx_partials/board_piece_moved.tpl.html",
        {
            "game_presenter": game_presenter,
            "board_id": board_id,
        },
    )


@require_safe
@cache_control(private=True)
@etag(_game_etag)
def htmx_game_select_piece(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    # TODO: validate this data
    piece_square = cast(Square, req.GET.get("square"))
    board_id = cast(str, req.GET.get("board_id"))

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
        selected_piece_square=piece_square,
    )

    return render(
        req,
        "chess/htmx_partials/board_piece_available_targets.tpl.html",
        {
            "game_presenter": game_presenter,
            "board_id": board_id,
        },
    )


@require_POST
def htmx_game_move_piece(req: HttpRequest, game_id: str, from_: Square, to: Square) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)

    game_move_piece(game=game, from_square=from_, to_square=to)

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
    )

    return render(
        req,
        "chess/htmx_partials/board_piece_moved.tpl.html",
        {
            "game_presenter": game_presenter,
        },
    )


@require_POST
def htmx_game_bot_move(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    if not game.is_versus_bot:
        raise SuspiciousOperation("This game has no bot")
    if game.bot_side != game.active_player:
        raise SuspiciousOperation("This is not bot's turn")

    bot_next_move = get_bot_next_move(fen=game.fen, bot_side=game.bot_side)
    game_move_piece(game=game, from_square=bot_next_move[0], to_square=bot_next_move[1])

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
    )

    return render(
        req,
        "chess/htmx_partials/board_piece_moved.tpl.html",
        {
            "game_presenter": game_presenter,
        },
    )

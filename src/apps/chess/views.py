from __future__ import annotations

from typing import TYPE_CHECKING, cast
from zlib import adler32

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag, require_POST, require_safe

from .components.pages.chess import chess_move_piece_htmx_fragment, chess_page, chess_select_piece_htmx_fragment
from .domain.queries import get_current_daily_challenge
from .domain.types import Square
from .models import DailyChallenge
from .presenters import GamePresenter

if TYPE_CHECKING:
    from django.http import HttpRequest


def _game_etag(req: HttpRequest) -> str | None:
    if settings.NO_HTTP_CACHE:
        return None
    # TODO: add the FEN from the user cookie, and then re-enable this cache
    return None

    hash_data = (
        game_id,
        req.path,
        str(int(Game.objects.filter(id=game_id).values_list("updated_at", flat=True).get().timestamp())),
    )
    return str(adler32("::".join(hash_data).encode("utf-8")))


@require_safe
@etag(_game_etag)
def game_view(req: HttpRequest) -> HttpResponse:
    challenge = get_current_daily_challenge()
    board_id = "main"

    game_presenter = GamePresenter(
        game=challenge,
        my_side="w",  # TODO: de-hardcode this - should come from the user
        factions={"w": "humans", "b": "undeads"},  # TODO: de-hardcode this - should come from the game
    )

    return HttpResponse(chess_page(game_presenter=game_presenter, request=req, board_id=board_id))


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
        factions={"w": "humans", "b": "undeads"},  # TODO: de-hardcode this - should come from the game
    )

    # No pieces were actually moved here, but as this template renders the whole pieces and
    # an empty targets container we can just re-use it to display a "waiting_for_player_selection" board:
    return HttpResponse(chess_move_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id))


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
        factions={"w": "humans", "b": "undeads"},  # TODO: de-hardcode this - should come from the game
        selected_piece_square=piece_square,
    )

    return HttpResponse(
        chess_select_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id)
    )


@require_POST
def htmx_game_move_piece(req: HttpRequest, game_id: str, from_: Square, to: Square) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    board_id = cast(str, req.GET.get("board_id"))

    game_move_piece(game=game, from_=from_, to=to)

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
        factions={"w": "humans", "b": "undeads"},  # TODO: de-hardcode this - should come from the game
    )

    return HttpResponse(chess_move_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id))


@require_POST
def htmx_game_bot_move(req: HttpRequest, game_id: str) -> HttpResponse:
    game = get_object_or_404(Game, id=game_id)
    if not game.is_versus_bot:
        raise SuspiciousOperation("This game has no bot")
    if game.bot_side != game.active_player:
        raise SuspiciousOperation("This is not bot's turn")
    if not (move := req.GET.get("move")):  # TODO: move this to the view path
        raise Http404("Missing bot move")
    board_id = cast(str, req.GET.get("board_id"))

    bot_next_move = move[0:2], move[2:4]
    game_move_piece(game=game, from_=bot_next_move[0], to=bot_next_move[1])

    game_presenter = GamePresenter(
        game=game,
        my_side="w",  # TODO: de-hardcode this - should come from the user
        factions={"w": "humans", "b": "undeads"},  # TODO: de-hardcode this - should come from the game
    )

    return HttpResponse(chess_move_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id))

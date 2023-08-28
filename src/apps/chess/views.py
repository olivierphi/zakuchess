from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import etag, require_POST, require_safe

from .components.pages.chess import chess_move_piece_htmx_fragment, chess_page, chess_select_piece_htmx_fragment
from .domain.helpers import get_active_player_side_from_fen
from .domain.mutations import move_daily_challenge_piece
from .domain.queries import get_current_daily_challenge
from .domain.types import Square
from .presenters import GamePresenter
from .views_helpers import get_or_create_daily_challenge_state_for_player, save_daily_challenge_state_in_session

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .domain.daily_challenge import PlayerGameState
    from .models import DailyChallenge


_logger = logging.getLogger(__name__)


def _game_etag(req: "HttpRequest") -> str | None:
    if settings.NO_HTTP_CACHE:
        return None
    # TODO: add the FEN from the user cookie, and then re-enable this cache
    return None
    # from zlib import adler32
    #
    # hash_data = (
    #     game_id,
    #     req.path,
    #     str(int(Game.objects.filter(id=game_id).values_list("updated_at", flat=True).get().timestamp())),
    # )
    # return str(adler32("::".join(hash_data).encode("utf-8")))


@require_safe
@etag(_game_etag)
def game_view(req: "HttpRequest") -> HttpResponse:
    challenge = get_current_daily_challenge()
    board_id = "main"
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)

    if created:
        _logger.info("Created game state: %s", game_state)
        _logger.info("Let's play bot's first turn")
        # TODO: pre-compute this in the challenge model?
        piece_role_by_square = challenge.piece_role_by_square
        bot_from, bot_to = cast("Square", challenge.bot_first_move[0:2]), cast("Square", challenge.bot_first_move[2:4])
        piece_role_by_square[bot_from] = piece_role_by_square[bot_to]
        del piece_role_by_square[bot_to]
        game_state = {
            "fen": challenge.fen_before_bot_first_move,
            "piece_role_by_square": piece_role_by_square,
        }
        forced_bot_move = (bot_from, bot_to)
        save_daily_challenge_state_in_session(
            request=req,
            challenge_id=challenge.id,
            game_state=game_state,
        )
    else:
        forced_bot_move = None

    _logger.info("Game state from player cookie: %s", game_state)

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
        forced_bot_move=forced_bot_move,
    )

    return HttpResponse(chess_page(game_presenter=game_presenter, request=req, board_id=board_id))


@require_safe
@etag(_game_etag)
def htmx_game_no_selection(req: "HttpRequest") -> HttpResponse:
    # TODO: validate this data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    board_id = "main"
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        raise SuspiciousOperation("Can't cancel selection without a started game")

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
    )

    # No pieces were actually moved here, but as this template renders the whole pieces and
    # an empty targets container we can just re-use it to display a "waiting_for_player_selection" board:
    return HttpResponse(chess_move_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id))


@require_safe
@etag(_game_etag)
def htmx_game_select_piece(req: "HttpRequest") -> "HttpResponse":
    # TODO: validate this data, using a Form
    piece_square = cast(Square, req.GET.get("square"))
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        raise SuspiciousOperation("Can't select a piece without a started game")

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
        selected_piece_square=piece_square,
    )

    return HttpResponse(
        chess_select_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id)
    )


@require_POST
def htmx_game_move_piece(req: HttpRequest, from_: Square, to: Square) -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    previous_game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        raise SuspiciousOperation("Can't play without a previously started game")

    _logger.info("Game state from player cookie: %s", previous_game_state)

    new_game_state = move_daily_challenge_piece(game_state=previous_game_state, from_=from_, to=to)
    _logger.info("New game state: %s", new_game_state)
    save_daily_challenge_state_in_session(
        request=req,
        challenge_id=challenge.id,
        game_state=new_game_state,
    )

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=new_game_state,
    )

    return HttpResponse(chess_move_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id))


@require_POST
def htmx_game_bot_move(req: HttpRequest) -> HttpResponse:
    # TODO: validate this data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        raise SuspiciousOperation("Can't play against the bot without a previously started game")

    _logger.info("Game state from player cookie: %s", game_state)

    active_player_side = get_active_player_side_from_fen(game_state["fen"])
    if active_player_side != challenge.bot_side:
        raise SuspiciousOperation("This is not bot's turn")

    if not (move := req.GET.get("move")):  # TODO: move this to the view path
        raise Http404("Missing bot move")

    return _play_bot_move(
        req=req,
        challenge=challenge,
        game_state=game_state,
        move=move,
        board_id=board_id,
    )


def _play_bot_move(
    *,
    req: "HttpRequest",
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
    move: str,
    board_id: str,
) -> HttpResponse:
    bot_next_move = cast("Square", move[0:2]), cast("Square", move[2:4])
    new_game_state = move_daily_challenge_piece(game_state=game_state, from_=bot_next_move[0], to=bot_next_move[1])
    save_daily_challenge_state_in_session(
        request=req,
        challenge_id=challenge.id,
        game_state=new_game_state,
    )

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=new_game_state,
    )

    return HttpResponse(chess_move_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id))

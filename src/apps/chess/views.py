import logging
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import etag, require_POST, require_safe

from .business_logic import get_current_daily_challenge, move_daily_challenge_piece
from .business_logic.types import Square
from .components.pages.chess import chess_moving_parts_fragment, chess_page, chess_select_piece_htmx_fragment
from .helpers import get_active_player_side_from_fen, uci_move_squares
from .presenters import GamePresenter
from .views_helpers import get_or_create_daily_challenge_state_for_player, save_daily_challenge_state_in_session

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .business_logic.daily_challenge import PlayerGameState
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
        game_state["fen"] = challenge.fen_before_bot_first_move
        game_state["piece_role_by_square"] = challenge.piece_role_by_square_before_bot_first_move

        save_daily_challenge_state_in_session(
            request=req,
            challenge_id=challenge.id,
            game_state=game_state,
        )

        forced_bot_move = uci_move_squares(challenge.bot_first_move)
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
        return redirect("chess:daily_game_view")

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
    )

    return HttpResponse(
        chess_moving_parts_fragment(game_presenter=game_presenter, request=req, board_id=board_id),
    )


@require_safe
@etag(_game_etag)
def htmx_game_select_piece(req: "HttpRequest") -> "HttpResponse":
    # TODO: validate this data, using a Form
    piece_square = cast(Square, req.GET.get("square"))
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        return redirect("chess:daily_game_view")

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
        selected_piece_square=piece_square,
    )

    return HttpResponse(
        chess_select_piece_htmx_fragment(game_presenter=game_presenter, request=req, board_id=board_id)
    )


@require_POST
def htmx_game_move_piece(req: "HttpRequest", from_: "Square", to: "Square") -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    previous_game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        return redirect("chess:daily_game_view")

    active_player_side = get_active_player_side_from_fen(previous_game_state["fen"])
    _logger.info("Game state from player cookie: %s", previous_game_state)

    new_game_state = move_daily_challenge_piece(game_state=previous_game_state, from_=from_, to=to)
    if active_player_side != challenge.bot_side:
        new_game_state["turns_counter"] += 1

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

    return HttpResponse(
        chess_moving_parts_fragment(game_presenter=game_presenter, request=req, board_id=board_id),
    )


@require_POST
def htmx_restart_daily_challenge_ask_confirmation(req: "HttpRequest") -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        return redirect("chess:daily_game_view")

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
        restart_daily_challenge_ask_confirmation=True,
    )

    return HttpResponse(
        chess_moving_parts_fragment(game_presenter=game_presenter, request=req, board_id=board_id),
    )


@require_POST
def htmx_restart_daily_challenge_do(req: "HttpRequest") -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        return redirect("chess:daily_game_view")

    # Restarting the daily challenge costs one move:
    game_state["turns_counter"] += 1
    # Back to the initial state:
    game_state["fen"] = challenge.fen_before_bot_first_move
    game_state["piece_role_by_square"] = challenge.piece_role_by_square_before_bot_first_move

    save_daily_challenge_state_in_session(
        request=req,
        challenge_id=challenge.id,
        game_state=game_state,
    )

    forced_bot_move = uci_move_squares(challenge.bot_first_move)

    game_presenter = GamePresenter(
        challenge=challenge,
        game_state=game_state,
        forced_bot_move=forced_bot_move,
    )

    return HttpResponse(
        chess_moving_parts_fragment(game_presenter=game_presenter, request=req, board_id=board_id),
    )


@require_POST
def htmx_game_bot_move(req: "HttpRequest") -> HttpResponse:
    # TODO: validate this data, using a Form
    board_id = cast(str, req.GET.get("board_id"))

    challenge = get_current_daily_challenge()
    game_state, created = get_or_create_daily_challenge_state_for_player(request=req, challenge=challenge)
    if created:
        return redirect("chess:daily_game_view")

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
    bot_next_move = uci_move_squares(move)
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

    return HttpResponse(
        chess_moving_parts_fragment(game_presenter=game_presenter, request=req, board_id=board_id),
    )

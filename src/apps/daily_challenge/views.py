import logging
from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_safe

from apps.chess.helpers import get_active_player_side_from_fen, uci_move_squares
from apps.chess.types import Square
from apps.utils.view_decorators import user_is_staff
from apps.utils.views_helpers import htmx_aware_redirect

from .business_logic import move_daily_challenge_piece
from .components.pages.chess import (
    daily_challenge_moving_parts_fragment,
    daily_challenge_page,
)
from .cookie_helpers import (
    get_or_create_daily_challenge_state_for_player,
    save_daily_challenge_state_in_session,
)
from .presenters import DailyChallengeGamePresenter

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .models import DailyChallenge
    from .types import PlayerGameState


_logger = logging.getLogger(__name__)

# TODO: extract game logic to a separate module


@require_safe
def game_view(request: "HttpRequest") -> HttpResponse:
    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    board_id = "main"
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )

    if created:
        # The player hasn't played this challenge before,
        # so we need to start from the beginning, with the bot's first move:
        game_state["fen"] = challenge.fen_before_bot_first_move
        game_state[
            "piece_role_by_square"
        ] = challenge.piece_role_by_square_before_bot_first_move

        save_daily_challenge_state_in_session(
            request=request,
            game_state=game_state,
        )

        forced_bot_move = uci_move_squares(challenge.bot_first_move)
    else:
        forced_bot_move = None

    _logger.info("Game state from player cookie: %s", game_state)

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=game_state,
        forced_bot_move=forced_bot_move,
        is_htmx_request=False,
        refresh_last_move=True,
        is_preview=is_preview,
    )

    return HttpResponse(
        daily_challenge_page(
            game_presenter=game_presenter, request=request, board_id=board_id
        )
    )


@require_safe
def htmx_game_no_selection(request: "HttpRequest") -> HttpResponse:
    # TODO: validate this data, using a Form
    board_id = cast(str, request.GET.get("board_id"))

    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    board_id = "main"
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )
    if created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=game_state,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


@require_safe
def htmx_game_select_piece(request: "HttpRequest") -> "HttpResponse":
    # TODO: validate this data, using a Form
    piece_square = cast(Square, request.GET.get("square"))
    board_id = cast(str, request.GET.get("board_id"))

    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )
    if created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=game_state,
        selected_piece_square=piece_square,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        )
    )


@require_POST
def htmx_game_move_piece(
    request: "HttpRequest", from_: "Square", to: "Square"
) -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, request.GET.get("board_id"))

    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    previous_game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )
    if created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    active_player_side = get_active_player_side_from_fen(previous_game_state["fen"])
    is_my_side = active_player_side != challenge.bot_side
    _logger.info("Game state from player cookie: %s", previous_game_state)

    new_game_state = move_daily_challenge_piece(
        game_state=previous_game_state, from_=from_, to=to, is_my_side=is_my_side
    )

    _logger.info("New game state: %s", new_game_state)
    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
    )

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=new_game_state,
        is_htmx_request=True,
        refresh_last_move=True,
    )

    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


@require_POST
def htmx_restart_daily_challenge_ask_confirmation(
    request: "HttpRequest",
) -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, request.GET.get("board_id"))

    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )
    if created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=game_state,
        restart_daily_challenge_ask_confirmation=True,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


@require_POST
def htmx_restart_daily_challenge_do(request: "HttpRequest") -> HttpResponse:
    # TODO: validate the whole data, using a Form
    board_id = cast(str, request.GET.get("board_id"))

    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )
    if created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_state["attempts_counter"] += 1
    game_state["current_attempt_turns_counter"] = 0
    # Restarting the daily challenge costs one move:
    game_state["turns_counter"] += 1
    # Back to the initial state:
    game_state["fen"] = challenge.fen_before_bot_first_move
    game_state[
        "piece_role_by_square"
    ] = challenge.piece_role_by_square_before_bot_first_move
    game_state["moves"] = ""

    save_daily_challenge_state_in_session(
        request=request,
        game_state=game_state,
    )

    forced_bot_move = uci_move_squares(challenge.bot_first_move)

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=game_state,
        forced_bot_move=forced_bot_move,
        is_htmx_request=True,
        refresh_last_move=True,
    )

    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


@require_POST
def htmx_game_bot_move(request: "HttpRequest") -> HttpResponse:
    # TODO: validate this data, using a Form
    board_id = cast(str, request.GET.get("board_id"))

    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )
    if created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    _logger.info("Game state from player cookie: %s", game_state)

    active_player_side = get_active_player_side_from_fen(game_state["fen"])
    if active_player_side != challenge.bot_side:
        # This is not bot's turn 😅
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    if not (move := request.GET.get("move")):  # TODO: move this to the view path
        raise Http404("Missing bot move")

    return _play_bot_move(
        request=request,
        challenge=challenge,
        game_state=game_state,
        move=move,
        board_id=board_id,
    )


@require_safe
@user_passes_test(user_is_staff)
def debug_reset_today(request: "HttpRequest") -> HttpResponse:
    # This function is dangerous, so let's make sure we're not using it
    # in another view accidentally 😅
    from .cookie_helpers import clear_daily_challenge_state_in_session

    clear_daily_challenge_state_in_session(request=request)

    return redirect("daily_challenge:daily_game_view")


@require_safe
@user_passes_test(user_is_staff)
def debug_view_cookie(request: "HttpRequest") -> HttpResponse:
    import json

    from .cookie_helpers import get_player_session_content

    player_cookie_content = get_player_session_content(request)
    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    game_state, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )

    return HttpResponse(
        f"""<p>Game state exists before check: {'no' if created else 'yes'}</p>"""
        f"""<p>Game keys: {tuple(player_cookie_content['games'].keys())}</p>"""
        f"""<p>Game_state: <pre>{json.dumps(game_state, indent=2)}</pre></p>"""
        f"""<p>admin_daily_challenge_lookup_key: <pre>{request.get_signed_cookie('admin_daily_challenge_lookup_key', default=None)}</pre></p>"""
    )


def _play_bot_move(
    *,
    request: "HttpRequest",
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
    move: str,
    board_id: str,
) -> HttpResponse:
    bot_next_move = uci_move_squares(move)
    new_game_state = move_daily_challenge_piece(
        game_state=game_state,
        from_=bot_next_move[0],
        to=bot_next_move[1],
        is_my_side=False,
    )

    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
    )

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=new_game_state,
        is_bot_move=True,
        is_htmx_request=True,
        refresh_last_move=True,
    )

    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


def get_current_daily_challenge_or_admin_preview(
    request: "HttpRequest",
) -> tuple["DailyChallenge", bool]:
    from .business_logic import get_current_daily_challenge
    from .models import DailyChallenge

    if request.user.is_staff:
        admin_daily_challenge_lookup_key = request.get_signed_cookie(
            "admin_daily_challenge_lookup_key", default=None
        )
        if admin_daily_challenge_lookup_key:
            return (
                DailyChallenge.objects.get(lookup_key=admin_daily_challenge_lookup_key),
                True,
            )

    return get_current_daily_challenge(), False

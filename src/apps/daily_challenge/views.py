import functools
import logging
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect, resolve_url
from django.views.decorators.http import require_POST, require_safe
from django_htmx.http import HttpResponseClientRedirect

from apps.chess.helpers import get_active_player_side_from_fen, uci_move_squares
from apps.chess.types import (
    ChessInvalidActionException,
    ChessInvalidMoveException,
    Square,
)
from apps.utils.view_decorators import user_is_staff
from apps.utils.views_helpers import htmx_aware_redirect

from .business_logic import (
    manage_daily_challenge_defeat_logic,
    manage_daily_challenge_moved_piece_logic,
    manage_daily_challenge_victory_logic,
    move_daily_challenge_piece,
    restart_daily_challenge,
    see_daily_challenge_solution,
)
from .components.misc_ui.help_modal import help_modal
from .components.misc_ui.stats_modal import stats_modal
from .components.misc_ui.user_prefs_modal import user_prefs_modal
from .components.pages.daily_chess import (
    daily_challenge_moving_parts_fragment,
    daily_challenge_page,
)
from .cookie_helpers import (
    clear_daily_challenge_game_state_in_session,
    get_or_create_daily_challenge_state_for_player,
    save_daily_challenge_state_in_session,
    save_user_prefs,
)
from .forms import UserPrefsForm
from .models import PlayerGameOverState
from .presenters import DailyChallengeGamePresenter
from .view_helpers import get_current_daily_challenge_or_admin_preview
from .views_decorators import (
    handle_chess_logic_exceptions,
    redirect_if_game_not_started,
    with_game_context,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.chess.types import Move

    from .view_helpers import GameContext


_logger = logging.getLogger(__name__)


@require_safe
@with_game_context
def game_view(request: "HttpRequest", *, ctx: "GameContext") -> HttpResponse:
    if ctx.created:
        # The player hasn't played this challenge before,
        # so we need to start from the beginning, with the bot's first move:

        # These fields are always set on a published challenge:
        assert (
            ctx.challenge.fen_before_bot_first_move
            and ctx.challenge.piece_role_by_square_before_bot_first_move
        )

        ctx.game_state.fen = ctx.challenge.fen_before_bot_first_move
        ctx.game_state.piece_role_by_square = (
            ctx.challenge.piece_role_by_square_before_bot_first_move
        )

        save_daily_challenge_state_in_session(
            request=request,
            game_state=ctx.game_state,
            player_stats=ctx.stats,
        )

        forced_bot_move = uci_move_squares(ctx.challenge.bot_first_move)
        is_very_first_game = ctx.stats.games_count == 0
    else:
        forced_bot_move = None
        is_very_first_game = False

    _logger.info("Game state from player cookie: %s", ctx.game_state)

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        user_prefs=ctx.user_prefs,
        forced_bot_move=forced_bot_move,
        is_htmx_request=False,
        refresh_last_move=True,
        is_preview=ctx.is_preview,
        is_very_first_game=is_very_first_game,
    )

    return HttpResponse(
        daily_challenge_page(
            game_presenter=game_presenter, request=request, board_id=ctx.board_id
        )
    )


@require_safe
@with_game_context
@redirect_if_game_not_started
def htmx_game_no_selection(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        user_prefs=ctx.user_prefs,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_safe
@handle_chess_logic_exceptions
@with_game_context
@redirect_if_game_not_started
def htmx_game_select_piece(
    request: "HttpRequest", *, ctx: "GameContext", location: "Square"
) -> HttpResponse:
    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        user_prefs=ctx.user_prefs,
        selected_piece_square=location,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
@handle_chess_logic_exceptions
@with_game_context
@redirect_if_game_not_started
def htmx_game_move_piece(
    request: "HttpRequest", *, ctx: "GameContext", from_: "Square", to: "Square"
) -> HttpResponse:
    if from_ == to:
        raise ChessInvalidMoveException("Not a move")

    game_over_already = ctx.game_state.game_over != PlayerGameOverState.PLAYING

    if ctx.game_state.game_over != PlayerGameOverState.PLAYING:
        raise ChessInvalidActionException("Game is over, cannot move pieces")
    if ctx.game_state.solution_index is not None:
        raise ChessInvalidActionException(
            "'See solution' mode is active, cannot move pieces"
        )

    active_player_side = get_active_player_side_from_fen(ctx.game_state.fen)
    is_my_side = active_player_side != ctx.challenge.bot_side
    _logger.info("Game state from player cookie: %s", ctx.game_state)

    new_game_state, captured_piece_role = move_daily_challenge_piece(
        game_state=ctx.game_state, from_=from_, to=to, is_my_side=is_my_side
    )

    just_won, just_lost = False, False
    if not game_over_already:
        just_won = new_game_state.game_over == PlayerGameOverState.WON
        just_lost = new_game_state.game_over == PlayerGameOverState.LOST

    if just_won:
        # The player won! GGWP 🏆
        manage_daily_challenge_victory_logic(
            challenge=ctx.challenge,
            game_state=new_game_state,
            stats=ctx.stats,
            is_preview=ctx.is_preview,
        )
    elif just_lost:
        # Sorry - hopefully victory will be yours next time! 🤞
        manage_daily_challenge_defeat_logic(
            game_state=new_game_state, is_preview=ctx.is_preview
        )
    else:
        # Keep playing. Good luck!
        manage_daily_challenge_moved_piece_logic(
            game_state=new_game_state, stats=ctx.stats, is_preview=ctx.is_preview
        )

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=new_game_state,
        user_prefs=ctx.user_prefs,
        is_htmx_request=True,
        refresh_last_move=True,
        captured_team_member_role=captured_piece_role,
        just_won=just_won,
    )

    _logger.info("New game state: %s", new_game_state)
    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
        player_stats=ctx.stats,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_safe
@with_game_context
def htmx_daily_challenge_stats_modal(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    modal_content = stats_modal(stats=ctx.stats)

    return HttpResponse(str(modal_content))


@require_safe
@with_game_context
def htmx_daily_challenge_help_modal(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        user_prefs=ctx.user_prefs,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    modal_content = help_modal(game_presenter=game_presenter)

    return HttpResponse(str(modal_content))


@require_safe
@with_game_context
def htmx_daily_challenge_user_prefs_modal(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:

    modal_content = user_prefs_modal(user_prefs=ctx.user_prefs)

    return HttpResponse(str(modal_content))


@require_POST
@with_game_context
@redirect_if_game_not_started
def htmx_restart_daily_challenge_ask_confirmation(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    from .components.misc_ui.daily_challenge_bar import (
        daily_challenge_bar,
        retry_confirmation_display,
    )

    daily_challenge_bar_inner_content = retry_confirmation_display(
        board_id=ctx.board_id
    )

    return HttpResponse(
        daily_challenge_bar(
            game_presenter=None,
            inner_content=daily_challenge_bar_inner_content,
            board_id=ctx.board_id,
        )
    )


@require_POST
@with_game_context
@redirect_if_game_not_started
def htmx_restart_daily_challenge_do(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    new_game_state = restart_daily_challenge(
        challenge=ctx.challenge, game_state=ctx.game_state, is_preview=ctx.is_preview
    )

    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
        player_stats=ctx.stats,
    )

    forced_bot_move = uci_move_squares(ctx.challenge.bot_first_move)

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=new_game_state,
        user_prefs=ctx.user_prefs,
        forced_bot_move=forced_bot_move,
        is_htmx_request=True,
        refresh_last_move=True,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
def htmx_daily_challenge_user_prefs_save(request: "HttpRequest") -> HttpResponse:
    # As user preferences updates can have an impact on any part of the UI
    # (changing the way the chess board is displayed, for example), we'd better
    # reload the whole page after having saved preferences.
    response = HttpResponseClientRedirect(
        resolve_url("daily_challenge:daily_game_view")
    )

    form = UserPrefsForm(request.POST)
    if user_prefs := form.to_user_prefs():
        save_user_prefs(user_prefs=user_prefs, response=response)

    return response


@require_POST
@with_game_context
@redirect_if_game_not_started
def htmx_see_daily_challenge_solution_ask_confirmation(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    from .components.misc_ui.daily_challenge_bar import (
        daily_challenge_bar,
        see_solution_confirmation_display,
    )

    daily_challenge_bar_inner_content = see_solution_confirmation_display(
        board_id=ctx.board_id
    )

    return HttpResponse(
        daily_challenge_bar(
            game_presenter=None,
            inner_content=daily_challenge_bar_inner_content,
            board_id=ctx.board_id,
        )
    )


@require_POST
@with_game_context
@redirect_if_game_not_started
def htmx_see_daily_challenge_solution_do(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    new_game_state = see_daily_challenge_solution(
        challenge=ctx.challenge, game_state=ctx.game_state, is_preview=ctx.is_preview
    )

    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
        player_stats=ctx.stats,
    )

    forced_bot_move = uci_move_squares(ctx.challenge.solution[:4])

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=new_game_state,
        user_prefs=ctx.user_prefs,
        forced_bot_move=forced_bot_move,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
@with_game_context
@redirect_if_game_not_started
def htmx_see_daily_challenge_solution_play(
    request: "HttpRequest", *, ctx: "GameContext"
) -> HttpResponse:
    if (solution_index := ctx.game_state.solution_index) is None:
        # This is a fishy request 😅
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    try:
        target_move = _daily_challenge_move_for_solution_index(
            ctx.challenge.solution, solution_index
        )
    except IndexError:
        # Hum, that shouldn't happen 🤔
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    new_game_state, captured_piece_role = move_daily_challenge_piece(
        game_state=ctx.game_state,
        from_=target_move[0],
        to=target_move[1],
        is_my_side=False,
    )
    assert new_game_state.solution_index is not None
    new_game_state.solution_index += 1

    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
        player_stats=ctx.stats,
    )

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=new_game_state,
        user_prefs=ctx.user_prefs,
        is_htmx_request=True,
        refresh_last_move=True,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
@handle_chess_logic_exceptions
@with_game_context
@redirect_if_game_not_started
def htmx_game_bot_move(
    request: "HttpRequest", *, ctx: "GameContext", from_: "Square", to: "Square"
) -> HttpResponse:
    if from_ == to:
        raise ChessInvalidMoveException("Not a move")

    _logger.info("Game state from player cookie: %s", ctx.game_state)

    active_player_side = get_active_player_side_from_fen(ctx.game_state.fen)
    is_bot_turn = active_player_side == ctx.challenge.bot_side
    if not is_bot_turn:
        # It is not the bot's turn... something fishy is going on 😅
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    return _play_bot_move(
        request=request,
        ctx=ctx,
        move=f"{from_}{to}",
        board_id=ctx.board_id,
    )


@require_safe
@user_passes_test(user_is_staff)
@with_game_context
def debug_reset_today(request: "HttpRequest", *, ctx: "GameContext") -> HttpResponse:
    clear_daily_challenge_game_state_in_session(request=request, player_stats=ctx.stats)

    return redirect("daily_challenge:daily_game_view")


@require_safe
@user_passes_test(user_is_staff)
@with_game_context
def debug_reset_stats(request: "HttpRequest", *, ctx: "GameContext") -> HttpResponse:
    # This function is VERY dangerous, so let's make sure we're not using it
    # in another view accidentally 😅
    from .cookie_helpers import clear_daily_challenge_stats_in_session

    clear_daily_challenge_stats_in_session(request=request, game_state=ctx.game_state)

    return redirect("daily_challenge:daily_game_view")


@require_safe
@user_passes_test(user_is_staff)
def debug_view_cookie(request: "HttpRequest") -> HttpResponse:
    import msgspec

    from .cookie_helpers import get_player_session_content_from_request

    player_cookie_content = get_player_session_content_from_request(request)
    challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
    game_state, stats, created = get_or_create_daily_challenge_state_for_player(
        request=request, challenge=challenge
    )

    def format_struct(struct):
        return msgspec.json.format(msgspec.json.encode(struct).decode())

    return HttpResponse(
        f"""<p>Game state exists before check: {'no' if created else 'yes'}</p>"""
        "\n"
        f"""<p>Game keys: {tuple(player_cookie_content.games.keys())}</p>"""
        "\n"
        f"""<p>Game state: <pre>{format_struct(game_state)}</pre></p>"""
        "\n"
        f"""<p>Player stats: <pre>{format_struct(stats)}</pre></p>"""
        "\n"
        f"""<p>admin_daily_challenge_lookup_key: <pre>{request.get_signed_cookie('admin_daily_challenge_lookup_key', default=None)}</pre></p>"""
    )


def _play_bot_move(
    *,
    request: "HttpRequest",
    ctx: "GameContext",
    move: "Move",
    board_id: str,
) -> HttpResponse:
    game_over_already = ctx.game_state.game_over != PlayerGameOverState.PLAYING

    bot_next_move = uci_move_squares(move)
    new_game_state, captured_piece_role = move_daily_challenge_piece(
        game_state=ctx.game_state,
        from_=bot_next_move[0],
        to=bot_next_move[1],
        is_my_side=False,
    )

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=new_game_state,
        user_prefs=ctx.user_prefs,
        is_bot_move=True,
        is_htmx_request=True,
        refresh_last_move=True,
        captured_team_member_role=captured_piece_role,
    )

    just_lost = (
        not game_over_already and new_game_state.game_over == PlayerGameOverState.LOST
    )
    if just_lost:
        # Sorry - hopefully victory will be yours next time! 🤞
        manage_daily_challenge_defeat_logic(
            game_state=new_game_state, is_preview=ctx.is_preview
        )

    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
        player_stats=ctx.stats,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=board_id
    )


def _daily_challenge_moving_parts_fragment_response(
    *,
    game_presenter: DailyChallengeGamePresenter,
    request: "HttpRequest",
    board_id: str,
) -> HttpResponse:
    return HttpResponse(
        daily_challenge_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


@functools.lru_cache(maxsize=20)
def _daily_challenge_move_for_solution_index(
    challenge_solution: str, solution_index: int
) -> tuple["Square", "Square"]:
    return uci_move_squares(challenge_solution.split(",")[solution_index])

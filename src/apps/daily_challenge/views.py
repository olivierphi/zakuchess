import dataclasses
import logging
from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_safe

from apps.chess.helpers import get_active_player_side_from_fen, uci_move_squares
from apps.chess.types import (
    ChessInvalidActionException,
    ChessInvalidMoveException,
    ChessLogicException,
    Square,
)
from apps.utils.view_decorators import user_is_staff
from apps.utils.views_helpers import htmx_aware_redirect

from .business_logic import (
    manage_daily_challenge_defeat_logic,
    manage_daily_challenge_victory_logic,
    manage_new_daily_challenge_logic,
    move_daily_challenge_piece,
)
from .components.misc_ui.stats_modal import stats_modal
from .components.pages.chess import (
    daily_challenge_moving_parts_fragment,
    daily_challenge_page,
)
from .cookie_helpers import (
    get_or_create_daily_challenge_state_for_player,
    save_daily_challenge_state_in_session,
)
from .decorators import handle_chess_logic_exceptions
from .presenters import DailyChallengeGamePresenter
from .types import PlayerGameOverState

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.chess.types import Move

    from .models import DailyChallenge
    from .types import PlayerGameState, PlayerStats


_logger = logging.getLogger(__name__)


@require_safe
def game_view(request: "HttpRequest") -> HttpResponse:
    ctx = GameContext.create_from_request(request)

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
    else:
        forced_bot_move = None

    _logger.info("Game state from player cookie: %s", ctx.game_state)

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        forced_bot_move=forced_bot_move,
        is_htmx_request=False,
        refresh_last_move=True,
        is_preview=ctx.is_preview,
    )

    return HttpResponse(
        daily_challenge_page(
            game_presenter=game_presenter, request=request, board_id=ctx.board_id
        )
    )


@require_safe
def htmx_game_no_selection(request: "HttpRequest") -> HttpResponse:
    ctx = GameContext.create_from_request(request)

    if ctx.created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_safe
@handle_chess_logic_exceptions
def htmx_game_select_piece(
    request: "HttpRequest", location: "Square"
) -> "HttpResponse":
    ctx = GameContext.create_from_request(request)
    if ctx.created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        selected_piece_square=location,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
@handle_chess_logic_exceptions
def htmx_game_move_piece(
    request: "HttpRequest", from_: "Square", to: "Square"
) -> HttpResponse:
    if from_ == to:
        raise ChessInvalidMoveException("Not a move")

    ctx = GameContext.create_from_request(request)

    if ctx.game_state.game_over != PlayerGameOverState.PLAYING:
        raise ChessInvalidActionException("Game is over, cannot move pieces")

    if ctx.created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    active_player_side = get_active_player_side_from_fen(ctx.game_state.fen)
    is_my_side = active_player_side != ctx.challenge.bot_side
    _logger.info("Game state from player cookie: %s", ctx.game_state)

    new_game_state, captured_piece_role = move_daily_challenge_piece(
        game_state=ctx.game_state, from_=from_, to=to, is_my_side=is_my_side
    )

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=new_game_state,
        is_htmx_request=True,
        refresh_last_move=True,
        captured_team_member_role=captured_piece_role,
    )

    if game_presenter.is_game_over:
        game_phase = game_presenter.game_phase
        if game_phase == "game_over:won":
            # The player won! GGWP 🏆
            manage_daily_challenge_victory_logic(
                game_state=new_game_state, stats=ctx.stats
            )
        else:
            # Sorry - hopefully victory will be yours next time! 🤞
            manage_daily_challenge_defeat_logic(
                game_state=new_game_state, stats=ctx.stats
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
def htmx_daily_challenge_stats_modal(
    request: "HttpRequest",
) -> HttpResponse:
    ctx = GameContext.create_from_request(request)

    modal_content = stats_modal(ctx.stats)

    return HttpResponse(str(modal_content))


@require_POST
def htmx_restart_daily_challenge_ask_confirmation(
    request: "HttpRequest",
) -> HttpResponse:
    ctx = GameContext.create_from_request(request)

    if ctx.created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        restart_daily_challenge_ask_confirmation=True,
        is_htmx_request=True,
        refresh_last_move=False,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
def htmx_restart_daily_challenge_do(request: "HttpRequest") -> HttpResponse:
    ctx = GameContext.create_from_request(request)
    if ctx.created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    # These fields are always set on a published challenge:
    assert (
        ctx.challenge.fen_before_bot_first_move
        and ctx.challenge.piece_role_by_square_before_bot_first_move
    )

    game_state = ctx.game_state
    game_state.attempts_counter += 1
    game_state.current_attempt_turns_counter = 0
    # Restarting the daily challenge costs one move:
    game_state.turns_counter += 1
    # Back to the initial state:
    game_state.fen = ctx.challenge.fen_before_bot_first_move
    game_state.piece_role_by_square = (
        ctx.challenge.piece_role_by_square_before_bot_first_move
    )
    game_state.moves = ""

    save_daily_challenge_state_in_session(
        request=request,
        game_state=game_state,
        player_stats=ctx.stats,
    )

    forced_bot_move = uci_move_squares(ctx.challenge.bot_first_move)

    game_presenter = DailyChallengeGamePresenter(
        challenge=ctx.challenge,
        game_state=game_state,
        forced_bot_move=forced_bot_move,
        is_htmx_request=True,
        refresh_last_move=True,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=ctx.board_id
    )


@require_POST
@handle_chess_logic_exceptions
def htmx_game_bot_move(
    request: "HttpRequest", from_: "Square", to: "Square"
) -> HttpResponse:
    if from_ == to:
        raise ChessInvalidMoveException("Not a move")

    ctx = GameContext.create_from_request(request)

    if ctx.created:
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    _logger.info("Game state from player cookie: %s", ctx.game_state)

    active_player_side = get_active_player_side_from_fen(ctx.game_state.fen)
    if active_player_side != ctx.challenge.bot_side:
        # This is not bot's turn 😅
        return htmx_aware_redirect(request, "daily_challenge:daily_game_view")

    return _play_bot_move(
        request=request,
        challenge=ctx.challenge,
        game_state=ctx.game_state,
        player_stats=ctx.stats,
        move=f"{from_}{to}",
        board_id=ctx.board_id,
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
    import msgspec

    from .cookie_helpers import get_player_session_content

    player_cookie_content = get_player_session_content(request)
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
    challenge: "DailyChallenge",
    game_state: "PlayerGameState",
    player_stats: "PlayerStats",
    move: "Move",
    board_id: str,
) -> HttpResponse:
    bot_next_move = uci_move_squares(move)
    new_game_state, captured_piece_role = move_daily_challenge_piece(
        game_state=game_state,
        from_=bot_next_move[0],
        to=bot_next_move[1],
        is_my_side=False,
    )

    game_presenter = DailyChallengeGamePresenter(
        challenge=challenge,
        game_state=new_game_state,
        is_bot_move=True,
        is_htmx_request=True,
        refresh_last_move=True,
        captured_team_member_role=captured_piece_role,
    )

    if game_presenter.is_game_over:
        if game_presenter.game_phase == "game_over:won":
            raise ChessLogicException(
                "Player won during bot's turn, this should not happen"
            )
        # Sorry - hopefully victory will be yours next time! 🤞
        manage_daily_challenge_defeat_logic(
            game_state=new_game_state, stats=player_stats
        )

    save_daily_challenge_state_in_session(
        request=request,
        game_state=new_game_state,
        player_stats=player_stats,
    )

    return _daily_challenge_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id=board_id
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


@dataclasses.dataclass(frozen=True)
class GameContext:
    challenge: "DailyChallenge"

    is_preview: bool
    """if we're in admin preview mode"""
    game_state: "PlayerGameState"
    stats: "PlayerStats"
    created: bool
    """if the game state was created on the fly as we were initialising that object"""
    board_id: str = "main"

    @classmethod
    def create_from_request(cls, request: "HttpRequest") -> "GameContext":
        challenge, is_preview = get_current_daily_challenge_or_admin_preview(request)
        game_state, stats, created = get_or_create_daily_challenge_state_for_player(
            request=request, challenge=challenge
        )
        # TODO: validate the "board_id" data
        board_id = cast(str, request.GET.get("board_id", "main"))

        if created:
            manage_new_daily_challenge_logic(stats)

        return cls(
            challenge=challenge,
            is_preview=is_preview,
            game_state=game_state,
            stats=stats,
            created=created,
            board_id=board_id,
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

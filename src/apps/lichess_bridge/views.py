import asyncio
from typing import TYPE_CHECKING

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from . import cookie_helpers, lichess_api
from .authentication import (
    LichessTokenRetrievalProcessContext,
    check_csrf_state_from_oauth2_callback,
    fetch_lichess_token_from_oauth2_callback,
    get_lichess_token_retrieval_via_oauth2_process_starting_url,
)
from .components.misc_ui.user_profile_modal import user_profile_modal
from .components.pages import lichess_pages as lichess_pages
from .components.pages.lichess_pages import lichess_game_moving_parts_fragment
from .forms import LichessCorrespondenceGameCreationForm
from .models import LichessGameFullFromStreamWithMetadata
from .presenters import LichessCorrespondenceGamePresenter
from .views_decorators import (
    handle_chess_logic_exceptions,
    redirect_if_no_lichess_access_token,
    with_lichess_access_token,
    with_user_prefs,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.chess.models import UserPrefs
    from apps.chess.types import (
        ChessInvalidActionException,
        ChessInvalidMoveException,
        Square,
    )

    from .models import (
        LichessAccessToken,
        LichessAccountInformation,
        LichessGameId,
    )

# TODO: use Django message framework for everything that happens outside of the chess
#  board, so we can notify users of what's going on
#  (we don't use HTMX for these steps, which will make the display of such messages easier)


@require_safe
@with_lichess_access_token
async def lichess_home_page(
    request: "HttpRequest", lichess_access_token: "LichessAccessToken | None"
) -> HttpResponse:
    if not lichess_access_token:
        page_content = lichess_pages.lichess_no_account_linked_page(request=request)
    else:
        page_content = await _get_my_games_list_page_content(
            request=request,
            lichess_access_token=lichess_access_token,
        )

    return HttpResponse(page_content)


@require_safe
@with_lichess_access_token
@redirect_if_no_lichess_access_token
async def lichess_my_games_list_page(
    request: "HttpRequest", lichess_access_token: "LichessAccessToken"
) -> HttpResponse:
    page_content = await _get_my_games_list_page_content(
        request=request,
        lichess_access_token=lichess_access_token,
    )

    return HttpResponse(page_content)


@require_http_methods(["GET", "POST"])
@with_lichess_access_token
@redirect_if_no_lichess_access_token
async def lichess_game_create(
    request: "HttpRequest", *, lichess_access_token: "LichessAccessToken"
) -> HttpResponse:
    me = await _get_me_from_lichess(lichess_access_token)

    form_errors = {}
    if request.method == "POST":
        form = LichessCorrespondenceGameCreationForm(request.POST)
        if not form.is_valid():
            form_errors = form.errors
        else:
            async with lichess_api.get_lichess_api_client(
                access_token=lichess_access_token
            ) as lichess_api_client:
                # N.B. This function returns a Lichess "Seek ID",
                # but we don't use it atm.
                await lichess_api.create_correspondence_game(
                    api_client=lichess_api_client,
                    days_per_turn=form.cleaned_data["days_per_turn"],
                )

            return redirect("lichess_bridge:homepage")

    return HttpResponse(
        lichess_pages.lichess_correspondence_game_creation_page(
            request=request, me=me, form_errors=form_errors
        )
    )


@require_safe
@with_lichess_access_token
@with_user_prefs
@redirect_if_no_lichess_access_token
async def lichess_correspondence_game_page(
    request: "HttpRequest",
    *,
    lichess_access_token: "LichessAccessToken",
    game_id: "LichessGameId",
    user_prefs: "UserPrefs | None",
) -> HttpResponse:
    me, game_data = await _get_game_context_from_lichess(
        lichess_access_token, game_id, use_game_cache=False
    )
    game_presenter = LichessCorrespondenceGamePresenter(
        game_data=game_data,
        is_htmx_request=False,
        refresh_last_move=True,
        user_prefs=user_prefs,
    )

    return HttpResponse(
        lichess_pages.lichess_correspondence_game_page(
            request=request,
            me=me,
            game_presenter=game_presenter,
        )
    )


@require_safe
@with_lichess_access_token
@with_user_prefs
@redirect_if_no_lichess_access_token
async def htmx_lichess_correspondence_game_no_selection(
    request: "HttpRequest",
    *,
    lichess_access_token: "LichessAccessToken",
    game_id: "LichessGameId",
    user_prefs: "UserPrefs | None",
) -> HttpResponse:
    me, game_data = await _get_game_context_from_lichess(lichess_access_token, game_id)
    game_presenter = LichessCorrespondenceGamePresenter(
        game_data=game_data,
        is_htmx_request=True,
        refresh_last_move=False,
        user_prefs=user_prefs,
    )

    return _lichess_game_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id="main"
    )


@require_safe
@with_lichess_access_token
@with_user_prefs
@redirect_if_no_lichess_access_token
@handle_chess_logic_exceptions
async def htmx_game_select_piece(
    request: "HttpRequest",
    *,
    lichess_access_token: "LichessAccessToken",
    game_id: "LichessGameId",
    location: "Square",
    user_prefs: "UserPrefs | None",
) -> HttpResponse:
    me, game_data = await _get_game_context_from_lichess(lichess_access_token, game_id)
    game_presenter = LichessCorrespondenceGamePresenter(
        game_data=game_data,
        selected_piece_square=location,
        is_htmx_request=True,
        refresh_last_move=False,
        user_prefs=user_prefs,
    )

    return _lichess_game_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id="main"
    )


@require_POST
@with_lichess_access_token
@with_user_prefs
@redirect_if_no_lichess_access_token
@handle_chess_logic_exceptions
async def htmx_game_move_piece(
    request: "HttpRequest",
    *,
    lichess_access_token: "LichessAccessToken",
    game_id: "LichessGameId",
    from_: "Square",
    to: "Square",
    user_prefs: "UserPrefs | None",
) -> HttpResponse:
    if from_ == to:
        raise ChessInvalidMoveException("Not a move")

    me, game_data = await _get_game_context_from_lichess(lichess_access_token, game_id)

    if not game_data.raw_data.is_ongoing_game:
        raise ChessInvalidActionException("Game is over, cannot move pieces")

    is_my_turn = game_data.players_from_my_perspective.active_player == "me"
    if not is_my_turn:
        raise ChessInvalidMoveException("Not my turn")

    async with lichess_api.get_lichess_api_client(
        access_token=lichess_access_token
    ) as lichess_api_client:
        move_was_successful = await lichess_api.move_lichess_game_piece(
            api_client=lichess_api_client, game_id=game_id, from_=from_, to=to
        )
        if not move_was_successful:
            raise ChessInvalidMoveException(
                f"Move '{from_}{to}' on game '{game_id}' was not successful on Lichess' side"
            )
        # The move was successful, let's re-fetch the updated game state:
        # (the cache for this game's data has be cleared by `move_lichess_game_piece`)
        game_data_raw = await lichess_api.get_game_by_id_from_stream(
            api_client=lichess_api_client,
            game_id=game_id,
            try_fetching_from_cache=False,
        )

    # TODO: handle end of game after move!

    game_data = LichessGameFullFromStreamWithMetadata(
        raw_data=game_data_raw, my_player_id=me.id
    )
    game_presenter = LichessCorrespondenceGamePresenter(
        game_data=game_data,
        is_htmx_request=True,
        refresh_last_move=True,
        user_prefs=user_prefs,
    )

    return _lichess_game_moving_parts_fragment_response(
        game_presenter=game_presenter, request=request, board_id="main"
    )


@require_safe
@with_lichess_access_token
@redirect_if_no_lichess_access_token
async def htmx_user_account_modal(
    request: "HttpRequest",
    *,
    lichess_access_token: "LichessAccessToken",
) -> HttpResponse:
    me = await _get_me_from_lichess(lichess_access_token)

    modal_content = user_profile_modal(request=request, me=me)

    return HttpResponse(str(modal_content))


@require_POST
def lichess_redirect_to_oauth2_flow_starting_url(
    request: "HttpRequest",
) -> HttpResponse:
    lichess_oauth2_process_context = LichessTokenRetrievalProcessContext.create_afresh(
        zakuchess_hostname=request.get_host(),
        zakuchess_protocol=request.scheme,
    )
    target_url = get_lichess_token_retrieval_via_oauth2_process_starting_url(
        context=lichess_oauth2_process_context
    )

    response = HttpResponseRedirect(target_url)
    # We will need to re-use some of this context's data in the webhook below:
    # --> let's store that in an HTTP-only cookie
    cookie_helpers.store_oauth2_token_retrieval_context_in_response_cookie(
        context=lichess_oauth2_process_context, response=response
    )

    return response


@require_safe
def lichess_webhook_oauth2_token_callback(request: "HttpRequest") -> HttpResponse:
    # Retrieve a context from the HTTP-only cookie we created above:
    lichess_oauth2_process_context = (
        cookie_helpers.get_oauth2_token_retrieval_context_from_request(request)
    )
    if lichess_oauth2_process_context is None:
        # TODO: Do something with that error
        return redirect("lichess_bridge:homepage")

    # We have to check the "CSRF state":
    # ( https://stack-auth.com/blog/oauth-from-first-principles#attack-4 )
    # TODO: add a test that checks that it does fail if the state doesn't match
    check_csrf_state_from_oauth2_callback(
        request=request, context=lichess_oauth2_process_context
    )

    # Ok, now let's fetch an API access token from Lichess!
    token = fetch_lichess_token_from_oauth2_callback(
        authorization_callback_response_url=request.get_full_path(),
        context=lichess_oauth2_process_context,
    )

    response = redirect("lichess_bridge:homepage")

    # OAuth2 flow is done: let's delete the cookie related to this flow:
    cookie_helpers.delete_oauth2_token_retrieval_context_from_cookies(response)

    # Now that we have an access token to interact with Lichess' API on behalf
    # of the user, let's store it into a long-lived HTTP-only cookie:
    cookie_helpers.store_lichess_api_access_token_in_response_cookie(
        token=token,
        response=response,
    )

    return response


@require_POST
def lichess_detach_account(request: "HttpRequest") -> HttpResponse:
    response = redirect("lichess_bridge:homepage")

    cookie_helpers.delete_lichess_api_access_token_from_cookies(response=response)

    return response


def _lichess_game_moving_parts_fragment_response(
    *,
    game_presenter: LichessCorrespondenceGamePresenter,
    request: "HttpRequest",
    board_id: str,
) -> HttpResponse:
    return HttpResponse(
        lichess_game_moving_parts_fragment(
            game_presenter=game_presenter, request=request, board_id=board_id
        ),
    )


async def _get_my_games_list_page_content(
    *,
    request: "HttpRequest",
    lichess_access_token: "LichessAccessToken",
) -> str:
    async with lichess_api.get_lichess_api_client(
        access_token=lichess_access_token
    ) as lichess_api_client:
        # As the queries are unrelated, let's run them in parallel:
        async with asyncio.TaskGroup() as tg:
            me = tg.create_task(
                lichess_api.get_my_account(api_client=lichess_api_client)
            )
            ongoing_games = tg.create_task(
                lichess_api.get_my_ongoing_games(api_client=lichess_api_client)
            )

    return lichess_pages.lichess_my_current_games_list_page(
        request=request,
        me=me.result(),
        ongoing_games=ongoing_games.result(),
    )


async def _get_me_from_lichess(
    lichess_access_token: "LichessAccessToken",
) -> "LichessAccountInformation":
    async with lichess_api.get_lichess_api_client(
        access_token=lichess_access_token
    ) as lichess_api_client:
        return await lichess_api.get_my_account(api_client=lichess_api_client)


async def _get_game_context_from_lichess(
    lichess_access_token: "LichessAccessToken",
    game_id: "LichessGameId",
    use_game_cache: bool = True,
) -> tuple["LichessAccountInformation", "LichessGameFullFromStreamWithMetadata"]:
    async with lichess_api.get_lichess_api_client(
        access_token=lichess_access_token
    ) as lichess_api_client:
        # As the queries are unrelated, let's run them in parallel:
        async with asyncio.TaskGroup() as tg:
            me_task = tg.create_task(
                lichess_api.get_my_account(api_client=lichess_api_client)
            )
            game_data_task = tg.create_task(
                lichess_api.get_game_by_id_from_stream(
                    api_client=lichess_api_client,
                    game_id=game_id,
                    try_fetching_from_cache=use_game_cache,
                )
            )

    me, game_data = me_task.result(), game_data_task.result()

    return me, LichessGameFullFromStreamWithMetadata(
        raw_data=game_data, my_player_id=me.id
    )

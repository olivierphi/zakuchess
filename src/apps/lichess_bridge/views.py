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
from .components.pages import lichess_pages as lichess_pages
from .forms import LichessCorrespondenceGameCreationForm
from .views_decorators import (
    redirect_if_no_lichess_access_token,
    with_lichess_access_token,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

    from .models import LichessAccessToken

# TODO: use Django message framework for everything that happens outside of the chess
#  board, so we can notify users of what's going on
#  (we don't use HTMX for these steps, which will make the display of such messages easier)


@require_safe
@with_lichess_access_token
async def lichess_home(
    request: "HttpRequest", lichess_access_token: "LichessAccessToken | None"
) -> HttpResponse:
    if not lichess_access_token:
        page_content = lichess_pages.lichess_no_account_linked_page(request=request)
    else:
        page_content = await lichess_pages.lichess_account_linked_homepage(
            request=request,
            access_token=lichess_access_token,
        )

    return HttpResponse(page_content)


@require_http_methods(["GET", "POST"])
@with_lichess_access_token
@redirect_if_no_lichess_access_token
async def lichess_correspondence_game_create(
    request: "HttpRequest", lichess_access_token: "LichessAccessToken"
) -> HttpResponse:
    form_errors = {}
    if request.method == "POST":
        form = LichessCorrespondenceGameCreationForm(request.POST)
        if not form.is_valid():
            form_errors = form.errors
        else:
            # N.B. This function returns a Lichess "Seek ID", but we don't use it atm.
            await lichess_api.create_correspondence_game(
                access_token=lichess_access_token,
                days_per_turn=form.cleaned_data["days_per_turn"],
            )

            return redirect("lichess_bridge:homepage")

    return HttpResponse(
        lichess_pages.lichess_correspondence_game_creation_page(
            request=request, form_errors=form_errors
        )
    )


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

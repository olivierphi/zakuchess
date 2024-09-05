from typing import TYPE_CHECKING

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST

from . import cookie_helpers
from .authentication import (
    LichessTokenRetrievalProcessContext,
    extract_lichess_token_from_oauth2_callback_url,
    get_lichess_token_retrieval_via_oauth2_process_starting_url,
)
from .components.pages.lichess import (
    lichess_account_linked_homepage,
    lichess_no_account_linked_page,
)

if TYPE_CHECKING:
    from django.http import HttpRequest


@require_GET
def lichess_home(request: "HttpRequest") -> HttpResponse:
    # Do we have a Lichess API token for this user?
    lichess_access_token = cookie_helpers.get_lichess_api_access_token_from_request(
        request
    )

    if not lichess_access_token:
        page_content = lichess_no_account_linked_page(request=request)
    else:
        page_content = lichess_account_linked_homepage(
            request=request,
            access_token=lichess_access_token,
        )

    return HttpResponse(page_content)


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


@require_GET
def lichess_webhook_oauth2_token_callback(request: "HttpRequest") -> HttpResponse:
    # Retrieve a context from the HTTP-only cookie we created above:
    lichess_oauth2_process_context = (
        cookie_helpers.get_oauth2_token_retrieval_context_from_request(request)
    )
    if lichess_oauth2_process_context is None:
        # TODO: Do something with that error
        return redirect("lichess_bridge:homepage")

    token = extract_lichess_token_from_oauth2_callback_url(
        authorization_callback_response_url=request.get_full_path(),
        context=lichess_oauth2_process_context,
    )

    response = redirect("lichess_bridge:homepage")

    # OAuth2 flow is done: let's delete the cookie related to this flow:
    cookie_helpers.delete_oauth2_token_retrieval_context_from_cookies(response)

    # Now that we have an access token to interact with Lichess' API on behalf
    # of the user, let's store it into a HTTP-only cookie:
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

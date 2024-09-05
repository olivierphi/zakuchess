from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from .authentication import (
    LichessTokenRetrievalProcessContext,
    extract_lichess_token_from_oauth2_callback_url,
)
from .components.pages.lichess import lichess_no_account_linked_page
from .cookie_helpers import (
    delete_oauth2_token_retrieval_context_from_cookies,
    get_oauth2_token_retrieval_context_from_request,
    store_oauth2_token_retrieval_context_in_response_cookie,
)

if TYPE_CHECKING:
    from django.http import HttpRequest


def lichess_home(request: "HttpRequest") -> HttpResponse:
    lichess_oauth2_process_context = LichessTokenRetrievalProcessContext.create_afresh(
        zakuchess_hostname=request.get_host(),
        zakuchess_protocol=request.scheme,
    )

    response = HttpResponse(
        lichess_no_account_linked_page(
            request=request,
            lichess_oauth2_process_context=lichess_oauth2_process_context,
        )
    )
    # We will need to re-use some of this context's data in the webhook below:
    # --> let's store that in an HTTP-only cookie
    store_oauth2_token_retrieval_context_in_response_cookie(
        context=lichess_oauth2_process_context, response=response
    )

    return response


@require_GET
def lichess_webhook_oauth2_token_callback(request: "HttpRequest") -> HttpResponse:
    # Retrieve a context from the HTTP-only cookie we created above:
    lichess_oauth2_process_context = get_oauth2_token_retrieval_context_from_request(
        request
    )
    if lichess_oauth2_process_context is None:
        # TODO: Do something with that error
        return redirect("lichess_bridge:homepage")

    token = extract_lichess_token_from_oauth2_callback_url(
        authorization_callback_response_url=request.get_full_path(),
        context=lichess_oauth2_process_context,
    )

    response = HttpResponse(f"{token=}")
    delete_oauth2_token_retrieval_context_from_cookies(response)

    return response

import logging
from typing import TYPE_CHECKING

from msgspec import MsgspecError

from .authentication import LichessTokenRetrievalProcessContext

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_NAME = "lichess.oauth2.ctx"
# One day should be more than enough to let the user grant their authorisation:
_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_MAX_AGE = 3600 * 24


_logger = logging.getLogger(__name__)


def store_oauth2_token_retrieval_context_in_response_cookie(
    *, context: LichessTokenRetrievalProcessContext, response: "HttpResponse"
) -> None:
    """
    Store OAuth2 token retrieval context into a response cookie.
    """

    response.set_cookie(
        _OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_NAME,
        context.to_cookie_content(),
        max_age=_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_MAX_AGE,
        httponly=True,
    )


def get_oauth2_token_retrieval_context_from_request(
    request: "HttpRequest",
) -> LichessTokenRetrievalProcessContext | None:
    """
    Returns a context created from the "CSRF state" and "code verifier" found in the request's cookie.
    """
    cookie_content: str | None = request.COOKIES.get(
        _OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_NAME
    )
    if not cookie_content:
        return None

    try:
        context = LichessTokenRetrievalProcessContext.from_cookie_content(
            cookie_content,
            zakuchess_hostname=request.get_host(),
            zakuchess_protocol=request.scheme,
        )
        return context
    except MsgspecError:
        _logger.exception("Could not decode cookie content.")
        return None


def delete_oauth2_token_retrieval_context_from_cookies(
    response: "HttpResponse",
) -> None:
    response.delete_cookie(_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_NAME)

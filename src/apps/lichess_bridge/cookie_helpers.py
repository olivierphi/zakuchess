import logging
from typing import TYPE_CHECKING, cast

from django.core.exceptions import SuspiciousOperation
from msgspec import MsgspecError

from .authentication import LichessTokenRetrievalProcessContext
from .models import LICHESS_ACCESS_TOKEN_PREFIX

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from .authentication import LichessToken
    from .models import LichessAccessToken

_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE = {
    "name": "lichess.oauth2.ctx",
    # One day should be more than enough to let the user grant their authorisation:
    "max-age": 3600 * 24,
}

_API_ACCESS_TOKEN_COOKIE = {
    "name": "lichess.access_token",
    # Access tokens delivered by Lichess "are long-lived (expect one year)".
    # Let's store them for approximately 6 months, on our end:
    "max-age": 3600 * 24 * 30 * 6,
}


_logger = logging.getLogger(__name__)


def store_oauth2_token_retrieval_context_in_response_cookie(
    *, context: LichessTokenRetrievalProcessContext, response: "HttpResponse"
) -> None:
    """
    Store OAuth2 token retrieval context into a short-lived response cookie.
    """

    response.set_cookie(
        _OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE["name"],
        context.to_cookie_content(),
        max_age=_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE["max-age"],
        httponly=True,
        samesite="Lax",
    )


def get_oauth2_token_retrieval_context_from_request(
    request: "HttpRequest",
) -> LichessTokenRetrievalProcessContext | None:
    """
    Returns a context created from the "CSRF state" and "code verifier" found in the request's cookies.
    """
    cookie_content: str | None = request.COOKIES.get(
        _OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE["name"]
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
    response.delete_cookie(_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE["name"])


def store_lichess_api_access_token_in_response_cookie(
    *, token: "LichessToken", response: "HttpResponse"
) -> None:
    """
    Store a Lichess API token into a long-lived response cookie.
    """

    response.set_cookie(
        _API_ACCESS_TOKEN_COOKIE["name"],
        token.access_token,
        # TODO: should we use the token's `expires_in` here, rather than our custom
        #   expiry period? There are pros and cons, let's decide that later :-)
        max_age=_API_ACCESS_TOKEN_COOKIE["max-age"],
        httponly=True,
        samesite="Lax",
    )


def get_lichess_api_access_token_from_request(
    request: "HttpRequest",
) -> "LichessAccessToken | None":
    """
    Returns a Lichess API token found in the request's cookies.
    """
    cookie_content: str | None = request.COOKIES.get(_API_ACCESS_TOKEN_COOKIE["name"])
    if not cookie_content:
        return None

    if (
        not cookie_content.startswith(LICHESS_ACCESS_TOKEN_PREFIX)
        or len(cookie_content) < 10
    ):
        raise SuspiciousOperation(
            f"Suspicious Lichess API token value '{cookie_content}'"
        )

    return cast("LichessAccessToken", cookie_content)


def delete_lichess_api_access_token_from_cookies(
    response: "HttpResponse",
) -> None:
    response.delete_cookie(_API_ACCESS_TOKEN_COOKIE["name"])

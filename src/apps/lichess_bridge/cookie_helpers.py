import datetime as dt
import logging
from typing import TYPE_CHECKING, cast

from django.core.exceptions import SuspiciousOperation
from msgspec import MsgspecError

from lib.http_cookies_helpers import (
    HttpCookieAttributes,
    set_http_cookie_on_django_response,
)

from .authentication import LichessTokenRetrievalProcessContext
from .lichess_api import is_lichess_api_access_token_valid

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from .authentication import LichessToken
    from .models import LichessAccessToken

_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_ATTRS = HttpCookieAttributes(
    name="lichess.oauth2.ctx",
    # This cookie only has to be valid while the user is redirected to Lichess
    # and press the "Authorize" button there.
    max_age=dt.timedelta(hours=1),
    http_only=True,
    same_site="Lax",
)

_API_ACCESS_TOKEN_COOKIE_ATTRS = HttpCookieAttributes(
    name="lichess.access_token",
    # Access tokens delivered by Lichess "are long-lived (expect one year)".
    # As Lichess gives us the expiry date of the tokens it gives us, we can use that
    # for our own cookie - so no "max-age" entry here, but we'll specify one at runtime.
    max_age=None,
    http_only=True,
    same_site="Lax",
)


_logger = logging.getLogger(__name__)


def store_oauth2_token_retrieval_context_in_response_cookie(
    *, context: LichessTokenRetrievalProcessContext, response: "HttpResponse"
) -> None:
    """
    Store OAuth2 token retrieval context into a short-lived response cookie.
    """

    set_http_cookie_on_django_response(
        response=response,
        attributes=_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_ATTRS,
        value=context.to_cookie_content(),
    )


def get_oauth2_token_retrieval_context_from_request(
    request: "HttpRequest",
) -> LichessTokenRetrievalProcessContext | None:
    """
    Returns a context created from the "CSRF state" and "code verifier" found in the request's cookies.
    """
    cookie_content: str | None = request.COOKIES.get(
        _OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_ATTRS.name
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
    response.delete_cookie(_OAUTH2_TOKEN_RETRIEVAL_CONTEXT_COOKIE_ATTRS.name)


def store_lichess_api_access_token_in_response_cookie(
    *, token: "LichessToken", response: "HttpResponse"
) -> None:
    """
    Store a Lichess API token into a long-lived response cookie.
    """
    # TODO: use a secured cookie here?

    # Our cookie will expire when the access token given by Lichess will:
    cookie_attributes = _API_ACCESS_TOKEN_COOKIE_ATTRS._replace(
        max_age=dt.timedelta(seconds=token.expires_in),
    )

    set_http_cookie_on_django_response(
        response=response,
        attributes=cookie_attributes,
        value=token.access_token,
    )


def get_lichess_api_access_token_from_request(
    request: "HttpRequest",
) -> "LichessAccessToken | None":
    """
    Returns a Lichess API token found in the request's cookies.
    """
    cookie_content: str | None = request.COOKIES.get(
        _API_ACCESS_TOKEN_COOKIE_ATTRS.name
    )
    if not cookie_content:
        return None

    if not is_lichess_api_access_token_valid(cookie_content):
        raise SuspiciousOperation(
            f"Suspicious Lichess API token value '{cookie_content}'"
        )

    return cast("LichessAccessToken", cookie_content)


def delete_lichess_api_access_token_from_cookies(
    response: "HttpResponse",
) -> None:
    response.delete_cookie(_API_ACCESS_TOKEN_COOKIE_ATTRS.name)

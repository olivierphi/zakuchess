import datetime as dt
import logging
from typing import TYPE_CHECKING

from msgspec import MsgspecError

from apps.chess.models import UserPrefs
from lib.http_cookies_helpers import (
    HttpCookieAttributes,
    set_http_cookie_on_django_response,
)

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


_USER_PREFS_COOKIE_ATTRS = HttpCookieAttributes(
    name="uprefs",
    max_age=dt.timedelta(days=30 * 6),  # approximately 6 months
    http_only=True,
    same_site="Lax",
)

_logger = logging.getLogger(__name__)


def get_user_prefs_from_request(request: "HttpRequest") -> UserPrefs:
    def new_content():
        return UserPrefs()

    cookie_content: str | None = request.COOKIES.get(_USER_PREFS_COOKIE_ATTRS.name)
    if cookie_content is None or len(cookie_content) < 5:
        return new_content()

    try:
        user_prefs = UserPrefs.from_cookie_content(cookie_content)
        return user_prefs
    except MsgspecError:
        _logger.exception(
            "Could not decode cookie content; restarting with a blank one."
        )
        return new_content()


def save_user_prefs(*, user_prefs: "UserPrefs", response: "HttpResponse") -> None:
    set_http_cookie_on_django_response(
        response=response,
        attributes=_USER_PREFS_COOKIE_ATTRS,
        value=user_prefs.to_cookie_content(),
    )

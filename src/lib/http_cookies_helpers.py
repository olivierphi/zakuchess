from typing import TYPE_CHECKING, Literal, NamedTuple

if TYPE_CHECKING:
    import datetime as dt

    from django.http import HttpResponse


class HttpCookieAttributes(NamedTuple):
    name: str
    max_age: "dt.timedelta | None"
    http_only: bool
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value
    same_site: Literal["Strict", "Lax", "None", None] = "Lax"


def set_http_cookie_on_django_response(
    *, response: "HttpResponse", attributes: HttpCookieAttributes, value: str
) -> None:
    response.set_cookie(
        attributes.name,
        value,
        max_age=attributes.max_age,
        httponly=attributes.http_only,
        samesite=attributes.same_site,
    )

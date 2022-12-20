from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpResponse

    from .models import Game


def add_http_caching_headers(response: "HttpResponse", *, game: "Game", max_age: int = 3_600) -> "HttpResponse":
    response["Cache-Control"] = f"private max-age={max_age}"
    response["Last-Modified"] = game.updated_at
    return response

from typing import TYPE_CHECKING

from django.middleware.csrf import get_token as get_csrf_token
from dominate.tags import input_

if TYPE_CHECKING:
    from django.http import HttpRequest


def csrf_hidden_input(request: "HttpRequest") -> input_:
    return input_(
        type="hidden", name="csrfmiddlewaretoken", value=get_csrf_token(request)
    )

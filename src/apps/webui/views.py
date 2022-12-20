from typing import TYPE_CHECKING

from django.shortcuts import redirect
from django.views.decorators.http import require_safe

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@require_safe
def hello_chess_board(req: "HttpRequest") -> "HttpResponse":
    return redirect("/games/new/")

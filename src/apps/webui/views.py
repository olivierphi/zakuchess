from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, "webui/home_page.html")

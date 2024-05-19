from typing import TYPE_CHECKING, cast

from django.shortcuts import redirect, resolve_url
from django_htmx.http import HttpResponseClientRedirect

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse
    from django_htmx.middleware import HtmxDetails


def htmx_aware_redirect(request: "HttpRequest", url: str) -> "HttpResponse":
    htmx_details = cast("HtmxDetails", getattr(request, "htmx"))
    if htmx_details:
        return HttpResponseClientRedirect(resolve_url(url))
    return redirect(url)

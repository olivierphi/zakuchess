from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from .components.misc_ui.user_prefs_modal import user_prefs_modal
from .cookie_helpers import get_user_prefs_from_request, save_user_prefs
from .forms import UserPrefsForm

if TYPE_CHECKING:
    from django.http import HttpRequest


@require_http_methods(["HEAD", "GET", "POST"])
def htmx_user_prefs_modal(request: "HttpRequest") -> HttpResponse:
    if request.method == "POST":
        # As user preferences updates can have an impact on any part of the UI
        # (changing the way the chess board is displayed, for example), we'd better
        # reload the whole page after having saved preferences.
        response = HttpResponseClientRedirect("/")

        form = UserPrefsForm(request.POST)
        if user_prefs := form.to_user_prefs():
            save_user_prefs(user_prefs=user_prefs, response=response)

        return response

    user_prefs = get_user_prefs_from_request(request)
    modal_content = user_prefs_modal(user_prefs=user_prefs)

    return HttpResponse(str(modal_content))

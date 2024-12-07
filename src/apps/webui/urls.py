from django.urls import path

from . import views

app_name = "webui"

urlpatterns = [
    # User prefs
    path(
        "htmx/modals/user-prefs/",
        views.htmx_user_prefs_modal,
        name="htmx_modal_user_prefs",
    ),
]

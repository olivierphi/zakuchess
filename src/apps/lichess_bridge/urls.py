from django.urls import path

from . import views

app_name = "lichess_bridge"

urlpatterns = [
    path("", views.lichess_home, name="homepage"),
    path(
        "webhook/oauth2/token-callback/",
        views.lichess_webhook_oauth2_token_callback,
        name="oauth2_token_callback",
    ),
]

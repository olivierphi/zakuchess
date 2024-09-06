from django.urls import path

from . import views

app_name = "lichess_bridge"

urlpatterns = [
    path("", views.lichess_home, name="homepage"),
    # Game management Views:
    path(
        "games/new/",
        views.lichess_correspondence_game_create,
        name="create_correspondence_game",
    ),
    # OAuth2 Views:
    path(
        "oauth2/start-flow/",
        views.lichess_redirect_to_oauth2_flow_starting_url,
        name="oauth2_start_flow",
    ),
    path(
        "oauth2/webhook/token-callback/",
        views.lichess_webhook_oauth2_token_callback,
        name="oauth2_token_callback",
    ),
    path(
        "account/detach/",
        views.lichess_detach_account,
        name="detach_lichess_account",
    ),
]

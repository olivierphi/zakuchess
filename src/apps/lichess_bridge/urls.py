from django.urls import path

from . import views

app_name = "lichess_bridge"

urlpatterns = [
    path("", views.lichess_home, name="homepage"),
    # Game management Views:
    path(
        "games/new/",
        views.lichess_game_create,
        name="create_game",
    ),
    path(
        "games/correspondence/<str:game_id>/",
        views.lichess_correspondence_game,
        name="correspondence_game",
    ),
    # path(
    #     "htmx/games/correspondence/<str:game_id>/no-selection/",
    #     views.htmx_game_no_selection,
    #     name="htmx_game_no_selection",
    # ),
    path(
        "htmx/games/correspondence/<str:game_id>/pieces/<square:location>/select/",
        views.htmx_game_select_piece,
        name="htmx_game_select_piece",
    ),
    path(
        "htmx/games/correspondence/<str:game_id>/pieces/<square:from_>/move/<square:to>/",
        views.htmx_game_move_piece,
        name="htmx_game_move_piece",
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

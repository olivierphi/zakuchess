from django.urls import path

from . import views

app_name = "chess"

urlpatterns = [
    path("new/", views.game_new),
    path("<str:game_id>/", views.game_view),
    path("htmx/games/<str:game_id>/", views.htmx_game_no_selection, name="htmx_game_no_selection"),
    path(
        "htmx/<str:game_id>/pieces/select/",
        views.htmx_game_select_piece,
        name="htmx_game_select_piece",
    ),
    path(
        "htmx/<str:game_id>/pieces/<str:from_>/move/<str:to>/",
        views.htmx_game_move_piece,
        name="htmx_game_move_piece",
    ),
    path(
        "htmx/<str:game_id>/bot/move/",
        views.htmx_game_bot_move,
        name="htmx_game_bot_move",
    ),
]

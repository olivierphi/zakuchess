from django.urls import path

from . import views

app_name = "chess"

urlpatterns = [
    path("", views.game_view, name="daily_game_view"),
    path("htmx/no-selection", views.htmx_game_no_selection, name="htmx_game_no_selection"),
    path(
        "htmx/pieces/select/",
        views.htmx_game_select_piece,
        name="htmx_game_select_piece",
    ),
    path(
        "htmx/pieces/<str:from_>/move/<str:to>/",
        views.htmx_game_move_piece,
        name="htmx_game_move_piece",
    ),
    path(
        "htmx/bot/move/",
        views.htmx_game_bot_move,
        name="htmx_game_bot_move",
    ),
]

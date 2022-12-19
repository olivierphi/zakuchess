from django.urls import path

from . import views

app_name = "webui"

urlpatterns = [
    path("", views.hello_chess_board),
    path("games/new/", views.game_new),
    path("games/<str:game_id>/", views.game_view),
    path(
        "htmx/games/<str:game_id>/pieces/select/",
        views.htmx_game_select_piece,
        name="htmx_game_select_piece",
    ),
    path(
        "htmx/games/<str:game_id>/pieces/<str:from_>/move/<str:to>/",
        views.htmx_game_move_piece,
        name="htmx_game_move_piece",
    ),
    path(
        "htmx/games/<str:game_id>/bot/move/",
        views.htmx_game_bot_move,
        name="htmx_game_bot_move",
    ),
]

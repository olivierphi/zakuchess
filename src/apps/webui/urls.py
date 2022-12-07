from django.urls import path

from . import views

app_name = "webui"

urlpatterns = [
    path("", views.hello_chess_board),
    path("games/new/", views.game_new),
    path("games/new/", views.game_new),
    path("games/<str:game_id>/", views.game_view),
    path(
        "htmx/games/<str:game_id>/pieces/move/",
        views.htmx_game_move_piece,
        name="htmx_game_move_piece",
    ),
]

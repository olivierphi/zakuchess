from django.urls import path

from . import views

urlpatterns = [
    path("", views.hello_chess_board),
    path("games/new/", views.game_new),
    path("games/new/", views.game_new),
    path("games/<str:game_id>/", views.game_view),
    path("htmx/games/<str:game_id>/pieces/<str:piece_square>/selection/", views.htmx_game_select_piece),
    path("htmx/games/<str:game_id>/pieces/<str:from_square>/move/<str:to_square>/", views.htmx_game_move_piece),
]

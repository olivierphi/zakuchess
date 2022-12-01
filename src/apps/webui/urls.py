from django.urls import path

from . import views

app_name = "webui"

urlpatterns = [
    path("", views.hello_chess_board),
    path("games/new/", views.game_new),
    path("games/new/", views.game_new),
    path("games/<str:game_id>/", views.game_view),
    path("games/<str:game_id>/move", views.action_game_move_piece),
    path("games/<str:game_id>/move/result", views.action_game_move_piece_result, name="action_game_move_piece_result"),
    # path("htmx/games/<str:game_id>/pieces/<str:piece_square>/selection/", views.htmx_game_select_piece),
    # path("htmx/games/<str:game_id>/pieces/<str:from_square>/move/<str:to_square>/", views.htmx_game_move_piece),
]

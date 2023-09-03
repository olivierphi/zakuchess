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
        "htmx/daily-challenge/restart/ask-confirmation/",
        views.htmx_restart_daily_challenge_ask_confirmation,
        name="htmx_restart_daily_challenge_ask_confirmation",
    ),
    path(
        "htmx/daily-challenge/restart/do/",
        views.htmx_restart_daily_challenge_do,
        name="htmx_restart_daily_challenge_do",
    ),
    path(
        "htmx/bot/move/",
        views.htmx_game_bot_move,
        name="htmx_game_bot_move",
    ),
    path("debug/reset-today", views.debug_reset_today),
    path("debug/view-cookie", views.debug_view_cookie),
]

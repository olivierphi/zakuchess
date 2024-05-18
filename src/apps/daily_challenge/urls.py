from django.urls import path

from . import views

app_name = "daily_challenge"

urlpatterns = [
    # Core game views
    path(
        "",
        views.game_view,
        name="daily_game_view",
    ),
    path(
        "htmx/no-selection/",
        views.htmx_game_no_selection,
        name="htmx_game_no_selection",
    ),
    path(
        "htmx/pieces/<square:location>/select/",
        views.htmx_game_select_piece,
        name="htmx_game_select_piece",
    ),
    path(
        "htmx/pieces/<square:from_>/move/<square:to>/",
        views.htmx_game_move_piece,
        name="htmx_game_move_piece",
    ),
    # Modals
    path(
        "htmx/daily-challenge/modals/stats/",
        views.htmx_daily_challenge_stats_modal,
        name="htmx_daily_challenge_modal_stats",
    ),
    path(
        "htmx/daily-challenge/modals/user-prefs/",
        views.htmx_daily_challenge_user_prefs_modal,
        name="htmx_daily_challenge_modal_user_prefs",
    ),
    path(
        "htmx/daily-challenge/modals/help/",
        views.htmx_daily_challenge_help_modal,
        name="htmx_daily_challenge_modal_help",
    ),
    # Restart views
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
    # Undo views
    path(
        "htmx/daily-challenge/undo/ask-confirmation/",
        views.htmx_undo_last_move_ask_confirmation,
        name="htmx_undo_last_move_ask_confirmation",
    ),
    path(
        "htmx/daily-challenge/undo/do/",
        views.htmx_undo_last_move_do,
        name="htmx_undo_last_move_do",
    ),
    # User prefs views
    path(
        "htmx/daily-challenge/user-prefs/",
        views.htmx_daily_challenge_user_prefs_save,
        name="htmx_daily_challenge_user_prefs_save",
    ),
    # "See the solution" views
    path(
        "htmx/daily-challenge/see-solution/ask-confirmation/",
        views.htmx_see_daily_challenge_solution_ask_confirmation,
        name="htmx_see_daily_challenge_solution_ask_confirmation",
    ),
    path(
        "htmx/daily-challenge/see-solution/do/",
        views.htmx_see_daily_challenge_solution_do,
        name="htmx_see_daily_challenge_solution_do",
    ),
    path(
        "htmx/daily-challenge/see-solution/play/",
        views.htmx_see_daily_challenge_solution_play,
        name="htmx_see_daily_challenge_solution_play",
    ),
    # Bot-related views
    path(
        "htmx/bot/pieces/<square:from_>/move/<square:to>/",
        views.htmx_game_bot_move,
        name="htmx_game_bot_move",
    ),
    # Debug views (staff only)
    path("debug/reset-today/", views.debug_reset_today),
    path("debug/reset-all-stats/", views.debug_reset_stats),
    path("debug/view-cookie/", views.debug_view_cookie),
]

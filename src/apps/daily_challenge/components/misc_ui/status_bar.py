from typing import TYPE_CHECKING

from dominate.tags import b, button, div, p
from dominate.util import raw

from apps.chess.helpers import (
    piece_name_from_piece_role,
    player_side_from_piece_role,
    type_from_piece_role,
)
from apps.daily_challenge.components.misc_ui.help import (
    character_type_tip,
    chess_status_bar_tip,
    chess_unit_symbol_display,
    help_content,
    unit_display_container,
)

from .common_styles import BUTTON_CLASSES

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from apps.daily_challenge.presenters import DailyChallengeGamePresenter


def status_bar(
    *, game_presenter: "DailyChallengeGamePresenter", board_id: str, **extra_attrs: str
) -> "dom_tag":
    from apps.chess.components.chess_board import INFO_BARS_COMMON_CLASSES

    # TODO: split this function into smaller ones

    inner_content: dom_tag = div("status to implement")

    if game_presenter.solution_index is not None:
        inner_content = div(
            p("See you tomorrow for another challenge! 🙂", cls="text-center"),
            cls="w-full",
        )
    elif game_presenter.is_intro_turn:
        inner_content = div(
            help_content(
                challenge_solution_turns_count=game_presenter.challenge_solution_turns_count,
                factions_tuple=tuple(game_presenter.factions.items()),
            ),
            div(
                button(
                    "⇧ Scroll up to the board",
                    cls=BUTTON_CLASSES,
                    onclick="""window.scrollTo({ top: 0, behavior: "smooth" })""",
                ),
                cls="w-full flex justify-center",
            ),
        )
    else:
        match game_presenter.game_phase:
            case "game_over:won":
                total_turns_counter = game_presenter.challenge_total_turns_counter + 1
                turns_counter = (
                    game_presenter.challenge_current_attempt_turns_counter + 1
                )
                attempts_counter = game_presenter.challenge_attempts_counter + 1
                msg = raw(
                    "Today it took you "
                    f"<b>{total_turns_counter}</b> turns, "
                    f"across <b>{attempts_counter}</b> "
                    f"attempt{'s' if attempts_counter > 1 else ''}."
                )
                inner_content = div(
                    div(raw(f"You won in <b>{turns_counter} turns</b>! 🎉")),
                    div(msg),
                    cls="w-full text-center",
                )
            case "game_over:lost":
                inner_content = div(
                    p("You lost! 😔"),
                    p(
                        "But you can try again, with the 'retry' button above! 🙂",
                        cls="w-full text-center",
                    ),
                    cls="w-full text-center",
                )
            case "waiting_for_player_selection":
                inner_content = chess_status_bar_tip(factions=game_presenter.factions)
            case "waiting_for_player_target_choice" | "opponent_piece_selected":
                inner_content = _chess_status_bar_selected_piece(game_presenter)
            case "waiting_for_bot_turn":
                inner_content = _chess_status_bar_waiting_for_bot_turn(game_presenter)

    return div(
        inner_content,
        id=f"chess-board-status-bar-{board_id}",
        cls=f"min-h-[4rem] flex items-center {INFO_BARS_COMMON_CLASSES} border-t-0 rounded-b-md",
        **extra_attrs,
    )


def _chess_status_bar_selected_piece(
    game_presenter: "DailyChallengeGamePresenter",
) -> "dom_tag":
    assert game_presenter.selected_piece is not None

    selected_piece = game_presenter.selected_piece
    team_member = selected_piece.team_member
    piece_role = selected_piece.piece_role
    player_side = player_side_from_piece_role(piece_role)
    piece_name = piece_name_from_piece_role(piece_role)

    unit_display = unit_display_container(
        piece_role=piece_role, factions=game_presenter.factions
    )
    team_member_name = team_member.get("name", "")
    name_display = (
        " ".join(team_member_name)
        if isinstance(team_member_name, list)
        else team_member_name
    )

    unit_about = div(
        div("> ", b(name_display, cls="text-yellow-400"), " <"),
        div(
            character_type_tip(type_from_piece_role(piece_role)),
            chess_unit_symbol_display(player_side=player_side, piece_name=piece_name),
        ),
        cls="grow text-center",
    )

    classes = (
        "flex",
        "w-full",
        "justify-between",
        "items-center",
        "flex-row" if selected_piece.player_side == "w" else "flex-row-reverse",
    )

    return div(
        unit_display,
        unit_about,
        div(
            cls="h-16 aspect-square", aria_hidden=True
        ),  # just to make the "about" centered visually
        cls=" ".join(classes),
    )


def _chess_status_bar_waiting_for_bot_turn(
    game_presenter: "DailyChallengeGamePresenter",
) -> "dom_tag":
    return div("Waiting for opponent's turn 🛡", cls="w-full text-center items-center")

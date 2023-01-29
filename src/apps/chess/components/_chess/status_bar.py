from typing import TYPE_CHECKING

from dominate.tags import div, dom_tag, img, span

from ...domain.consts import PLAYER_SIDES
from ...domain.helpers import (
    piece_name_from_piece_role,
    piece_name_from_piece_type,
    player_side_from_piece_role,
    utf8_symbol_from_piece_role,
)
from ..chess_helpers import chess_unit_symbol_url

if TYPE_CHECKING:
    from ...presenters import GamePresenter


def chess_status_bar(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    inner_content: dom_tag = div("status to implement")
    match game_presenter.game_phase:
        case "waiting_for_player_selection":
            inner_content = _chess_status_bar_score(game_presenter)
        case "waiting_for_player_target_choice" | "opponent_piece_selected":
            inner_content = _chess_status_bar_selected_piece(game_presenter)
        case "waiting_for_bot_turn":
            inner_content = _chess_status_bar_waiting_for_bot_turn(game_presenter)

    return div(
        inner_content,
        id=f"chess-board-status-bar-{board_id}",
        cls="h-16 flex items-stretch items-center text-slate-100 bg-chess-square-dark border-4 border-solid rounded-b-lg border-chess-square-light",
        **extra_attrs,
    )


def _chess_status_bar_score(game_presenter: "GamePresenter") -> dom_tag:
    turn_display = f"Turn {game_presenter.turn_number}. "

    score = game_presenter.score
    score_display = "No players leading at the moment"
    if score != 0:
        i_am_leading = score > 0 and game_presenter.my_side == "w" or score < 0 and game_presenter.my_side == "b"
        score_display = "".join(("You're" if i_am_leading else "Opponent is", f" leading by {abs(score)} points"))
        score_display += " 🙂" if i_am_leading else " 🙁"

    captured_pieces_to_display: tuple[list[str], list[str]] = ([], [])
    for i, player_side in enumerate(PLAYER_SIDES):
        for captured_piece in game_presenter.captured_pieces[player_side]:
            piece_name = piece_name_from_piece_type(captured_piece)
            captured_pieces_to_display[i].append(
                img(
                    src=chess_unit_symbol_url(player_side=player_side, piece_name=piece_name),
                    alt=piece_name,
                    cls="inline w-4 aspect-square",
                )
            )
    captures_display: list[str] = []
    if any(captured_pieces_to_display):
        my_captures_index = 1 if game_presenter.my_side == "w" else 0
        my_captures = captured_pieces_to_display[my_captures_index]
        captures_display += ("You captures: ",)
        if not my_captures:
            captures_display += ("nothing yet 😔",)
        else:
            captures_display += my_captures
        their_captures_index = 1 if my_captures_index == 0 else 0
        their_captures = captured_pieces_to_display[their_captures_index]
        captures_display += (" / ",)
        captures_display += ("Their captures: ",)
        if not my_captures:
            captures_display += ("nothing yet 😀",)
        else:
            captures_display += their_captures

    return div(div(turn_display, score_display), div(*captures_display), cls="w-full text-center")


def _chess_status_bar_selected_piece(game_presenter: "GamePresenter") -> dom_tag:
    from ..chess import chess_unit_display

    assert game_presenter.selected_piece is not None
    selected_piece = game_presenter.selected_piece
    team_member = selected_piece.team_member
    piece_role = selected_piece.piece_role
    player_side = player_side_from_piece_role(piece_role)
    piece_name = piece_name_from_piece_role(piece_role)

    unit_display = chess_unit_display(
        game_presenter=game_presenter,
        square=selected_piece.square,
        piece_role=piece_role,
    )
    unit_display_container = div(
        unit_display,
        cls="h-full aspect-square",
    )

    unit_about = div(
        div(f"{team_member.first_name} {team_member.last_name}"),
        div(
            f"Chess equivalent: ",
            img(
                src=chess_unit_symbol_url(player_side=player_side, piece_name=piece_name),
                alt=piece_name,
                cls="inline w-4 aspect-square",
            ),
        ),
        cls="grow text-center",
    )

    classes = [
        "flex",
        "w-full",
        "justify-between",
        "items-center",
        "flex-row" if selected_piece.player_side == "w" else "flex-row-reverse",
    ]

    return div(
        unit_display_container,
        unit_about,
        div(cls="h-full aspect-square", aria_hidden=True),  # just to make the "about" centered visually
        cls=" ".join(classes),
    )


def _chess_status_bar_waiting_for_bot_turn(game_presenter: "GamePresenter") -> dom_tag:
    return div("Your opponent 💻 is thinking of their next move", cls="w-full text-center")

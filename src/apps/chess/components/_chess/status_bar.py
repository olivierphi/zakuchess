import random
from typing import TYPE_CHECKING, cast

from dominate.tags import div, dom_tag, img
from dominate.util import raw

from ...domain.consts import PIECE_TYPE_TO_NAME
from ...domain.helpers import piece_name_from_piece_role, player_side_from_piece_role
from ..chess_helpers import chess_unit_symbol_url

if TYPE_CHECKING:
    from ...domain.types import PieceRole, PieceType, TeamMemberRole
    from ...presenters import GamePresenter


def chess_status_bar(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    from ..chess import INFO_BARS_COMMON_CLASSES

    inner_content: dom_tag = div("status to implement")
    match game_presenter.game_phase:
        case "waiting_for_player_selection":
            inner_content = _chess_status_bar_tip()
        case "waiting_for_player_target_choice" | "opponent_piece_selected":
            inner_content = _chess_status_bar_selected_piece(game_presenter)
        case "waiting_for_bot_turn":
            inner_content = _chess_status_bar_waiting_for_bot_turn(game_presenter)

    return div(
        inner_content,
        id=f"chess-board-status-bar-{board_id}",
        cls=f"min-h-[4rem] flex items-stretch items-center {INFO_BARS_COMMON_CLASSES} border-t-0 rounded-b-md",
        **extra_attrs,
    )


_CHARACTER_TYPE_TIP: dict["PieceType", str] = {
    "p": "swords",
    "n": "horses",
    "b": "bows",
    "r": "staffs",
    "q": "?",
    "k": "?",
}
_CHARACTER_TYPE_TIP_KEYS = tuple(_CHARACTER_TYPE_TIP.keys())

_CHARACTER_TYPE_ROLE_MAPPING: dict["PieceType", "TeamMemberRole"] = {
    "p": "p1",
    "n": "n1",
    "b": "b1",
    "r": "r1",
    "q": "q",
    "k": "k",
}


def _chess_status_bar_tip() -> dom_tag:
    character_type = random.choice(_CHARACTER_TYPE_TIP_KEYS)
    piece_name = PIECE_TYPE_TO_NAME[character_type]
    unit_left_side_role = cast("PieceRole", _CHARACTER_TYPE_ROLE_MAPPING[character_type].upper())
    unit_right_side_role = _CHARACTER_TYPE_ROLE_MAPPING[character_type]
    unit_display_left = _unit_display_container(unit_left_side_role)
    unit_display_right = _unit_display_container(unit_right_side_role)

    return div(
        unit_display_left,
        div(
            raw(f"💡 Characters with <b>{_CHARACTER_TYPE_TIP[character_type]}</b> are <b>{piece_name}s</b>"),
            img(
                src=chess_unit_symbol_url(player_side="w", piece_name=piece_name),
                alt=piece_name,
                cls="inline w-4 aspect-square",
            ),
            cls="text-center",
        ),
        unit_display_right,
        cls="flex w-full justify-between items-center",
    )


def _chess_status_bar_selected_piece(game_presenter: "GamePresenter") -> dom_tag:
    assert game_presenter.selected_piece is not None

    selected_piece = game_presenter.selected_piece
    team_member = selected_piece.team_member
    piece_role = selected_piece.piece_role
    player_side = player_side_from_piece_role(piece_role)
    piece_name = piece_name_from_piece_role(piece_role)

    unit_display = _unit_display_container(piece_role)

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
        unit_display,
        unit_about,
        div(cls="h-full aspect-square", aria_hidden=True),  # just to make the "about" centered visually
        cls=" ".join(classes),
    )


def _unit_display_container(piece_role: "PieceRole") -> dom_tag:
    from ..chess import chess_unit_display_with_ground_marker

    unit_display = chess_unit_display_with_ground_marker(
        piece_role=piece_role,
    )
    return div(
        unit_display,
        cls="h-full aspect-square",
    )


def _chess_status_bar_waiting_for_bot_turn(game_presenter: "GamePresenter") -> dom_tag:
    return div("Waiting for opponent's turn 💻 ", cls="w-full text-center items-center")

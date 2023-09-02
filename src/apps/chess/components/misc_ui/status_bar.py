import random
from functools import cache
from typing import TYPE_CHECKING, cast

from dominate.tags import div, dom_tag, h4, span
from dominate.util import raw

from apps.chess.helpers import piece_name_from_piece_role, player_side_from_piece_role, type_from_piece_role

from ...business_logic.consts import PIECE_TYPE_TO_NAME
from ..chess_helpers import chess_unit_symbol_class

if TYPE_CHECKING:
    from ...business_logic.types import Faction, Factions, PieceName, PieceRole, PieceType, PlayerSide, TeamMemberRole
    from ...presenters import GamePresenter


_CHARACTER_TYPE_TIP: dict["PieceType", str] = {
    "p": "Characters with <b>a sword</b>",
    "n": "<b>Mounted</b> characters",
    "b": "Characters with <b>a bow</b>",
    "r": "<b>Flying</b> characters",
    "q": "Characters with <b>a staff</b>",
    "k": "Characters wearing <b>a heavy armor</b>",
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


def chess_status_bar(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    from ..chess_board import INFO_BARS_COMMON_CLASSES

    inner_content: dom_tag = div("status to implement")
    align_items = "items-center"

    if game_presenter.is_bot_move and game_presenter.challenge_turns_counter == 0:
        inner_content = _first_turn_intro(
            challenge_total_turns=game_presenter.challenge_total_turns,
            factions_tuple=tuple(game_presenter.factions.items()),
        )
    else:
        match game_presenter.game_phase:
            case "game_over:won":
                inner_content = div(
                    div("You won! 🎉"),
                    div(raw(f"It took you <b>{game_presenter.challenge_turns_counter}</b> turns today.")),
                    cls="w-full text-center",
                )
            case "game_over:lost":
                inner_content = div("You lost! 😭", cls="w-full text-center")
            case "waiting_for_player_selection":
                inner_content = _chess_status_bar_tip(factions=game_presenter.factions)
                align_items = "items-stretch"
            case "waiting_for_player_target_choice" | "opponent_piece_selected":
                inner_content = _chess_status_bar_selected_piece(game_presenter)
                align_items = "items-stretch"
            case "waiting_for_bot_turn":
                inner_content = _chess_status_bar_waiting_for_bot_turn(game_presenter)

    return div(
        inner_content,
        id=f"chess-board-status-bar-{board_id}",
        cls=f"min-h-[4rem] flex {align_items} {INFO_BARS_COMMON_CLASSES} border-t-0 rounded-b-md",
        **extra_attrs,
    )


@cache
def _first_turn_intro(
    *, challenge_total_turns: int, factions_tuple: "tuple[tuple[PlayerSide, Faction], ...]"
) -> dom_tag:
    # N.B. We use a tuple here for the factions, so they're hashable and can be used as cached key
    return div(
        h4("Welcome to this new daily challenge!", cls="mb-2 text-amber-600 font-bold "),
        div("Tap one of your pieces to start playing.", cls="mb-2 font-bold"),
        div(raw(f"You have <b>{challenge_total_turns}</b> turns to win this challenge.")),
        div(raw("Your pieces are the ones <b>looking to the right</b>.")),
        div("Restarting from the beginning with the ↩️ button costs one turn."),
        div("Good luck! 🙂", cls="mt-2"),
        div(
            [
                _chess_status_bar_tip(factions=dict(factions_tuple), piece_type=piece_type, additional_classes="h-20")
                for piece_type in _CHARACTER_TYPE_TIP_KEYS
            ],
            cls="mt-2",
        ),
        cls="w-full text-center",
    )


def _chess_status_bar_tip(
    *, factions: "Factions", piece_type: "PieceType | None" = None, additional_classes: str = ""
) -> dom_tag:
    if piece_type is None:
        piece_type = random.choice(_CHARACTER_TYPE_TIP_KEYS)
    piece_name = PIECE_TYPE_TO_NAME[piece_type]
    unit_left_side_role = cast("PieceRole", _CHARACTER_TYPE_ROLE_MAPPING[piece_type].upper())
    unit_right_side_role = _CHARACTER_TYPE_ROLE_MAPPING[piece_type]
    unit_display_left = _unit_display_container(piece_role=unit_left_side_role, factions=factions)
    unit_display_right = _unit_display_container(piece_role=unit_right_side_role, factions=factions)

    return div(
        unit_display_left,
        div(
            _character_type_tip(piece_type),
            _chess_unit_symbol_display(player_side="b", piece_name=piece_name),
            cls="text-center",
        ),
        unit_display_right,
        cls=f"flex w-full justify-between items-center {additional_classes}",
    )


def _chess_status_bar_selected_piece(game_presenter: "GamePresenter") -> dom_tag:
    assert game_presenter.selected_piece is not None

    selected_piece = game_presenter.selected_piece
    team_member = selected_piece.team_member
    piece_role = selected_piece.piece_role
    player_side = player_side_from_piece_role(piece_role)
    piece_name = piece_name_from_piece_role(piece_role)

    unit_display = _unit_display_container(piece_role=piece_role, factions=game_presenter.factions)
    name_display = team_member.get("name", "")

    unit_about = div(
        div(name_display),
        div(
            _character_type_tip(type_from_piece_role(piece_role)),
            _chess_unit_symbol_display(player_side=player_side, piece_name=piece_name),
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
        div(cls="h-full aspect-square", aria_hidden=True),  # just to make the "about" centered visually
        cls=" ".join(classes),
    )


def _character_type_tip(piece_type: "PieceType") -> dom_tag:
    return raw(f"{_CHARACTER_TYPE_TIP[piece_type]} are chess <b>{PIECE_TYPE_TO_NAME[piece_type]}s</b>")


def _chess_unit_symbol_display(*, player_side: "PlayerSide", piece_name: "PieceName") -> dom_tag:
    classes = (
        "inline-block",
        "w-5",
        "align-text-bottom",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        chess_unit_symbol_class(player_side=player_side, piece_name=piece_name),
    )

    return span(
        cls=" ".join(classes),
    )


def _unit_display_container(*, piece_role: "PieceRole", factions: "Factions") -> dom_tag:
    from ..chess_board import chess_unit_display_with_ground_marker

    unit_display = chess_unit_display_with_ground_marker(
        piece_role=piece_role,
        factions=factions,
    )

    return div(
        unit_display,
        cls="h-full aspect-square",
    )


def _chess_status_bar_waiting_for_bot_turn(game_presenter: "GamePresenter") -> dom_tag:
    return div("Waiting for opponent's turn 💻 ", cls="w-full text-center items-center")

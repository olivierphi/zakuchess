from urllib.parse import urlencode
from typing import TYPE_CHECKING, cast

from chess import FILE_NAMES, RANK_NAMES
from django.urls import reverse
from dominate.tags import div, span, dom_tag

from .chess_helpers import square_to_tailwind_classes, piece_unit_classes, piece_player_side
from ..domain.types import Square

if TYPE_CHECKING:
    from ..presenters import GamePresenter
    from ..domain.types import PieceView, PlayerSide

_SQUARE_COLOR_TAILWIND_CLASSES = ("bg-chess-square-dark-color", "bg-chess-square-light-color")
_PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: dict["PlayerSide", str] = {
    "w": "bg-slate-100/40 border-slate-100",
    "b": "bg-slate-800/40 border-slate-800",
}


def chess_arena(*, game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    return div(
        div(
            chess_board(board_id),
            cls="absolute inset-0 pointer-events-none z-0",
            id=f"chess-board-container-{board_id}",
        ),
        div(
            chess_pieces(game_presenter=game_presenter, board_id=board_id),
            cls="absolute inset-0 pointer-events-none z-10",
            id=f"chess-pieces-container-{board_id}",
        ),
        div(
            chess_available_targets(game_presenter=game_presenter, board_id=board_id),
            cls="absolute inset-0 pointer-events-none z-20",
            id=f"chess-available-targets-container-{board_id}",
        ),
        id=f"chess-arena-{board_id}",
        cls="w-full md:max-w-xl mx-auto aspect-square relative border border-debug2 border-solid",
    )


def chess_board(board_id: str) -> dom_tag:
    squares: list[dom_tag] = []
    for file in FILE_NAMES:
        for rank in RANK_NAMES:
            squares.append(chess_board_square(cast(Square, f"{file}{rank}")))
    return div(
        *squares,
        id=f"chess-board-{board_id}",
        cls="relative aspect-square pointer-events-none border border-debug border-solid",
    )


def chess_pieces(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    pieces: list[dom_tag] = []
    for square, piece_view in game_presenter.pieces_view.items():
        pieces.append(
            chess_piece(square=square, piece_view=piece_view, game_presenter=game_presenter, board_id=board_id)
        )

    if game_presenter.is_bot_turn:
        bot_turn_attrs = dict(
            data_hx_post=f"{reverse('chess:htmx_game_bot_move', kwargs={'game_id': game_presenter.game_id})}?{urlencode({'board_id': board_id})}",
            data_hx_trigger="load delay:1s",
            data_hx_target=f"#chess-board-pieces-{ board_id }",
        )
    else:
        bot_turn_attrs = {}

    return div(
        *pieces,
        id=f"chess-board-pieces-{board_id}",
        cls="relative aspect-square border border-debug border-solid",
        **bot_turn_attrs,
        **extra_attrs,
    )


def chess_board_square(square: "Square") -> dom_tag:
    file, rank = square
    square_index = FILE_NAMES.index(file) + RANK_NAMES.index(rank)
    square_color_cls = _SQUARE_COLOR_TAILWIND_CLASSES[square_index % 2]
    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        square_color_cls,
        *square_to_tailwind_classes(square),
    ]
    square_info = span(
        "".join((file if rank == "1" else "", rank if file == "a" else "")),
        cls="text-chess-square-square-info",
    )
    return div(
        square_info,
        cls=" ".join(classes),
        # This one is for debugging purposes:
        data_square=square,
    )


def chess_piece(
    *, game_presenter: "GamePresenter", square: "Square", piece_view: "PieceView", board_id: str
) -> dom_tag:
    player_side = piece_player_side(piece_view)

    ground_marker = chess_unit_ground_marker(player_side=player_side)
    unit_display = chess_unit_display(game_presenter=game_presenter, square=square, piece_view=piece_view)

    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        *square_to_tailwind_classes(square),
        "transition-coordinates",
        "duration-200",
        "ease-in",
        "cursor-pointer",
        "pointer-events-auto",
    ]
    return div(
        ground_marker,
        unit_display,
        cls=" ".join(classes),
        id=f"board-{ board_id }-side-{ player_side }-piece-{ piece_view['id'] }",
        # htmx-related attributes:
        data_hx_trigger="click",
        data_hx_get=f"{reverse('chess:htmx_game_select_piece', kwargs={'game_id': game_presenter.game_id}) }?{urlencode({'square': square, 'board_id': board_id})}",
        data_hx_target=f"#chess-board-available-targets-{ board_id }",
        # These 2 are for debugging purposes:
        data_square=square,
        data_piece=piece_view["piece"],
    )


def chess_available_targets(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    children: list[dom_tag] = []
    if game_presenter.selected_piece:
        for square in game_presenter.selected_piece.available_targets:
            children.append(chess_available_target(game_presenter=game_presenter, square=square, board_id=board_id))

    return div(
        *children,
        cls="relative aspect-square pointer-events-none",
        id=f"chess-board-available-targets-{board_id}",
        **extra_attrs,
    )


def chess_available_target(*, game_presenter: "GamePresenter", square: "Square", board_id: str) -> dom_tag:
    target_marker = div(
        cls="w-1/5 h-1/5 rounded-full bg-chess-available-target-marker transition-size hover:w-1/4 hover:h-1/4 ",
    )
    target_marker_container = div(
        target_marker,
        cls="w-full aspect-square flex items-center justify-center",
    )
    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        *square_to_tailwind_classes(square),
        "cursor-pointer",
        "pointer-events-auto",
    ]
    return div(
        target_marker_container,
        cls=" ".join(classes),
        data_hx_post=f"{reverse('chess:htmx_game_move_piece', kwargs={'game_id': game_presenter.game_id, 'from_': game_presenter.selected_piece.square, 'to': square})}?{urlencode({'board_id': board_id})}",
        data_hx_target=f"#chess-board-pieces-{ board_id }",
        data_hx_swap="outerHTML",
    )


def chess_unit_display(*, game_presenter: "GamePresenter", square: "Square", piece_view: "PieceView") -> dom_tag:
    classes = [
        "relative",
        "w-full",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        "z-10",
        *piece_unit_classes(piece_view),
        # Conditional classes:
        *[
            "drop-shadow-selected-piece"
            if game_presenter.selected_piece and game_presenter.selected_piece.square == square
            else ""
        ],
        *[
            "drop-shadow-potential-capture"
            if game_presenter.selected_piece and game_presenter.selected_piece.is_potential_capture(square)
            else ""
        ],
    ]
    return div(
        cls=" ".join(classes),
    )


def chess_unit_ground_marker(*, player_side: "PlayerSide") -> dom_tag:
    classes = [
        "absolute",
        "w-5/6",
        "h-1/3",
        "left-1/12",
        "bottom-1",
        "rounded-1/2",
        "z-0",
        "border",
        "border-solid",
        _PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES[player_side],
    ]
    return div(
        cls=" ".join(classes),
    )

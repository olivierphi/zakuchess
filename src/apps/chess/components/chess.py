from urllib.parse import urlencode
from typing import TYPE_CHECKING

from chess import FILE_NAMES, RANK_NAMES
from django.urls import reverse
from dominate.tags import *

from .chess_helpers import square_to_tailwind_classes, piece_unit_classes

if TYPE_CHECKING:
    from ..presenters import GamePresenter
    from ..domain.types import PieceView

_SQUARE_COLOR_TAILWIND_CLASSES = ("bg-chess-square-dark-color", "bg-chess-square-light-color")


def chess_arena(*, game_presenter: "GamePresenter", board_id: str = "main") -> dom_tag:
    return div(
        div(chess_board(board_id), cls="absolute inset-0 pointer-events-none z-0"),
        div(
            chess_pieces(game_presenter=game_presenter, board_id=board_id),
            cls="absolute inset-0 pointer-events-none z-10",
        ),
        div(
            chess_available_targets(game_presenter=game_presenter, board_id=board_id),
            cls="absolute inset-0 pointer-events-none z-20",
        ),
        cls="w-full md:max-w-xl mx-auto aspect-square relative border border-debug2 border-solid",
    )


def chess_board(board_id: str) -> dom_tag:
    squares: list[dom_tag] = []
    for file in FILE_NAMES:
        for rank in RANK_NAMES:
            squares.append(chess_board_square(f"{file}{rank}"))
    return div(*squares, cls="relative aspect-square pointer-events-none border border-debug border-solid")


def chess_pieces(*, game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    pieces: list[dom_tag] = []
    for square, piece_view in game_presenter.pieces_view.items():
        pieces.append(
            chess_piece(square=square, piece_view=piece_view, game_presenter=game_presenter, board_id=board_id)
        )
    return div(
        *pieces,
        id=f"chess-board-available-targets-{board_id}",
        cls="relative aspect-square border border-debug border-solid",
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
        "".join((file if file == "a" else "", rank if rank == "1" else "")),
        cls="text-chess-square-square-info",
    )
    return div(square_info, data_square=square, cls=" ".join(classes))


def chess_piece(
    *, square: "Square", piece_view: "PieceView", game_presenter: "GamePresenter", board_id: str
) -> dom_tag:
    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        *square_to_tailwind_classes(square),
        *piece_unit_classes(piece_view),
        "transition-coordinates",
        "duration-300",
        "ease-in",
        "bg-no-repeat",
        "bg-cover",
        "cursor-pointer",
        "pointer-events-auto",
    ]
    return div(
        cls=" ".join(classes),
        data_square=square,
        data_piece=piece_view["piece"],
        # htmx-related attributes:
        data_hx_trigger="click",
        data_hx_get=f"{reverse('chess:htmx_game_select_piece', kwargs={'game_id': game_presenter.game_id}) }?{urlencode({'square': square, 'board_id': board_id})}",
        data_hx_target=f"#chess-board-available-targets-{ board_id }",
    )


def chess_available_targets(*, game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    return div(cls="relative aspect-square pointer-events-none", id=f"chess-board-available-targets-{board_id}")

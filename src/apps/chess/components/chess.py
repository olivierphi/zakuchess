import json
from string import Template
from typing import TYPE_CHECKING, cast
from urllib.parse import urlencode

from chess import FILE_NAMES, RANK_NAMES
from django.templatetags.static import static
from django.urls import reverse
from dominate.tags import div, dom_tag, span
from dominate.util import raw as unescaped_html

from ..domain.helpers import (
    file_and_rank_from_square,
    piece_name_from_piece_role,
    player_side_from_piece_role,
    type_from_piece_role,
)
from ._chess.score_bar import chess_score_bar
from ._chess.status_bar import chess_status_bar
from .chess_helpers import chess_square_color, chess_unit_symbol_url, piece_unit_classes, square_to_tailwind_classes

if TYPE_CHECKING:
    from ..domain.types import PieceRole, PlayerSide, Square
    from ..presenters import GamePresenter

_SQUARE_COLOR_TAILWIND_CLASSES = ("bg-chess-square-dark", "bg-chess-square-light")
_PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: dict[tuple["PlayerSide", bool], str] = {
    # the boolean says if the piece can move
    ("w", False): "bg-slate-100/40 border border-slate-100",
    ("b", False): "bg-slate-800/40 border border-slate-800",
    ("w", True): "bg-slate-100/40 border-2 border-chess-available-target-marker",
    ("b", True): "bg-slate-800/40 border-2 border-chess-available-target-marker",
}

_BOT_MOVE_DELAY = 500  # we'll wait that amount of millisecondes before starting the bot move's calculation
_PLAY_BOT_JS_TEMPLATE = Template(
    """
<script>
    (function () {
        setTimeout(function () {
            window.playBotMove("$FEN", "$PLAY_MOVE_HTMX_ELEMENT_ID", "$BOT_ASSETS_DATA_HOLDER_ELEMENT_ID");
        }, $MOVE_DELAY);
    })()</script>"""
)


def chess_arena(*, game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    return div(
        div(
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
            cls="aspect-square relative",
        ),
        chess_bot_data(board_id),
        chess_score_bar(game_presenter=game_presenter, board_id=board_id),
        chess_status_bar(game_presenter=game_presenter, board_id=board_id),
        id=f"chess-arena-{board_id}",
        cls="w-full md:max-w-xl mx-auto",
        # When the user clicks on anything that is not an interactive element of the chess board, and the state
        # of this chess board is not "waiting_for_player_selection", then the chess board is reset to this state.
        data_hx_get=f"{ reverse('chess:htmx_game_no_selection', kwargs={'game_id': game_presenter.game_id}) }?{ urlencode({'board_id': board_id}) }",
        data_hx_trigger=f"click[cursorIsNotOnChessBoardInteractiveElement('{ board_id }')] from:document",
        data_hx_target=f"#chess-board-pieces-{ board_id }",
    )


def chess_bot_data(board_id: str) -> dom_tag:
    stockfish_urls = {
        "wasm": static("chess/js/bot/stockfish.wasm.js"),
        "js": static("chess/js/bot/stockfish.js"),
    }
    return div(
        id=f"chess-bot-data-{board_id}",
        aria_hidden="true",
        data_stockfish_urls=json.dumps(stockfish_urls),
    )


def chess_board(board_id: str) -> dom_tag:
    squares: list[dom_tag] = []
    for file in FILE_NAMES:
        for rank in RANK_NAMES:
            squares.append(chess_board_square(cast("Square", f"{file}{rank}")))
    return div(
        *squares,
        id=f"chess-board-{board_id}",
        cls="relative aspect-square pointer-events-none",
    )


def chess_pieces(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    pieces: list[dom_tag] = []
    for square, piece_role in game_presenter.piece_role_by_square.items():
        pieces.append(
            chess_piece(square=square, piece_role=piece_role, game_presenter=game_presenter, board_id=board_id)
        )

    bot_turn_html_elements = _bot_turn_html_elements(game_presenter=game_presenter, board_id=board_id)

    return div(
        div(
            data_board_state=game_presenter.game_phase,
            data_aria_hidden="true",
        ),
        *pieces,
        *bot_turn_html_elements,
        id=f"chess-board-pieces-{board_id}",
        cls="relative aspect-square",
        **extra_attrs,
    )


def chess_board_square(square: "Square") -> dom_tag:
    file, rank = file_and_rank_from_square(square)
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
    *, game_presenter: "GamePresenter", square: "Square", piece_role: "PieceRole", board_id: str
) -> dom_tag:
    player_side = player_side_from_piece_role(piece_role)

    piece_can_move = (
        player_side == game_presenter.my_side and square in game_presenter.squares_with_pieces_that_can_move
    )
    ground_marker = chess_unit_ground_marker(player_side=player_side, can_move=piece_can_move)
    unit_display = chess_unit_display(piece_role=piece_role, game_presenter=game_presenter, square=square)
    unit_chess_symbol_display = chess_unit_symbol_display(piece_role=piece_role, square=square)

    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        *square_to_tailwind_classes(square),
        "cursor-pointer",
        "pointer-events-auto",
        # Transition-related classes:
        "transition-coordinates",
        "duration-300",
        "ease-in",
        "transform-gpu",
    ]
    return div(
        ground_marker,
        unit_display,
        unit_chess_symbol_display,
        cls=" ".join(classes),
        id=f"board-{ board_id }-side-{ player_side }-piece-{ piece_role }",
        # htmx-related attributes:
        data_hx_trigger="click",
        data_hx_get=f"{reverse('chess:htmx_game_select_piece', kwargs={'game_id': game_presenter.game_id}) }?{urlencode({'square': square, 'board_id': board_id})}",
        data_hx_target=f"#chess-board-available-targets-{ board_id }",
        # These 2 are mostly for debugging purposes:
        data_square=square,
        data_piece_role=piece_role,
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
    assert game_presenter.selected_piece is not None
    target_marker = div(
        cls="w-1/5 h-1/5 rounded-full bg-chess-available-target-marker transition-size hover:w-1/3 hover:h-1/3",
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
        # This one is mostly for debugging purposes:
        data_square=square,
    )


def chess_unit_display(
    *, piece_role: "PieceRole", game_presenter: "GamePresenter | None" = None, square: "Square | None" = None
) -> dom_tag:
    is_highlighted = (
        game_presenter
        and square
        and game_presenter.selected_piece
        and game_presenter.selected_piece.square == square
        and square in game_presenter.squares_with_pieces_that_can_move
    )
    classes = [
        "relative",
        "w-full",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        "z-10",
        *piece_unit_classes(piece_role),
        # Conditional classes:
        "drop-shadow-selected-piece" if is_highlighted else "",
        "drop-shadow-potential-capture"
        if game_presenter
        and game_presenter.selected_piece
        and game_presenter.selected_piece.is_potential_capture(square)
        else "",
    ]
    return div(
        cls=" ".join(classes),
    )


def chess_unit_ground_marker(*, player_side: "PlayerSide", can_move: bool = False) -> dom_tag:
    classes = [
        "absolute",
        "w-5/6",
        "h-1/3",
        "left-1/12",
        "bottom-1",
        "rounded-1/2",
        "z-0",
        "border-solid",
        _PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES[(player_side, can_move)],
    ]
    return div(
        cls=" ".join(classes),
    )


def chess_unit_display_with_ground_marker(*, piece_role: "PieceRole") -> dom_tag:
    player_side = player_side_from_piece_role(piece_role)

    ground_marker = chess_unit_ground_marker(player_side=player_side)
    unit_display = chess_unit_display(piece_role=piece_role)

    return div(
        ground_marker,
        unit_display,
        cls="relative h-full aspect-square",
    )


def chess_unit_symbol_display(*, piece_role: "PieceRole", square: "Square") -> dom_tag:
    player_side = player_side_from_piece_role(piece_role)
    piece_type = type_from_piece_role(piece_role)
    piece_name = piece_name_from_piece_role(piece_role)
    square_color = chess_square_color(square)

    symbol_class = (
        "w-10",
        "-ml-2" if piece_type == "n" else ("-ml-1" if player_side == "w" else "-mr-1"),
        # "-mt-1",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        "opacity-50" if square_color == "light" else "opacity-40",
    )
    symbol_display = div(
        style=f"background-image: url('{chess_unit_symbol_url(player_side='b', piece_name=piece_name)}')",
        cls=" ".join(symbol_class),
    )

    classes = (
        "absolute",
        "top-0",
        "left-0" if player_side == "w" else "right-0",
        "z-0",
        # Quick custom display for white knights, so they face the inside of the board:
        "-scale-x-100" if player_side == "w" and piece_type == "n" else "",
    )

    return div(
        symbol_display,
        cls=" ".join(classes),
        aria_label=piece_name,
    )


def _bot_turn_html_elements(*, game_presenter: "GamePresenter", board_id: str) -> list[dom_tag]:
    if not game_presenter.is_bot_turn:
        return []

    play_move_htmx_element_id = f"chess-bot-play-move-{ board_id }"
    return [
        unescaped_html(
            _PLAY_BOT_JS_TEMPLATE.safe_substitute(
                {
                    "FEN": game_presenter.fen,
                    "PLAY_MOVE_HTMX_ELEMENT_ID": play_move_htmx_element_id,
                    "BOT_ASSETS_DATA_HOLDER_ELEMENT_ID": f"chess-bot-data-{ board_id }",
                    "MOVE_DELAY": _BOT_MOVE_DELAY,
                }
            )
        ),
        div(
            id=play_move_htmx_element_id,
            data_hx_post=f"{reverse('chess:htmx_game_bot_move', kwargs={'game_id': game_presenter.game_id})}?{urlencode({'board_id': board_id, 'move': 'BOT_MOVE'})}",
            data_hx_target=f"#chess-board-pieces-{ board_id }",
            data_hx_trigger="playMove",
        ),
    ]

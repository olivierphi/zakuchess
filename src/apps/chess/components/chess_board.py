import json
from functools import cache
from string import Template
from typing import TYPE_CHECKING, cast
from urllib.parse import urlencode

from chess import FILE_NAMES, RANK_NAMES
from django.templatetags.static import static
from django.urls import reverse
from dominate.tags import div, dom_tag, span
from dominate.util import raw as unescaped_html

from apps.chess.helpers import (
    chess_square_color,
    file_and_rank_from_square,
    piece_name_from_piece_role,
    player_side_from_piece_role,
    type_from_piece_role,
)

from .chess_helpers import chess_unit_symbol_class, piece_character_classes, square_to_tailwind_classes
from .misc_ui.daily_challenge_bar import chess_daily_challenge_bar
from .misc_ui.status_bar import chess_status_bar

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..business_logic.types import Factions, PieceRole, PieceType, PlayerSide, Square
    from ..presenters import GamePresenter

SQUARE_COLOR_TAILWIND_CLASSES = ("bg-chess-square-dark", "bg-chess-square-light")
# SQUARE_COLOR_TAILWIND_CLASSES = ("bg-slate-600", "bg-zinc-400")
# SQUARE_COLOR_TAILWIND_CLASSES = ("bg-orange-600", "bg-orange-400")
INFO_BARS_COMMON_CLASSES = "text-slate-200 bg-slate-700 border-2 border-solid border-slate-400"
_PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: dict[tuple["PlayerSide", bool], str] = {
    # the boolean says if the piece can move
    ("w", False): "bg-slate-100/40 border border-slate-100",
    ("b", False): "bg-slate-800/40 border border-slate-800",
    ("w", True): "bg-slate-100/40 border-2 border-active-chess-available-target-marker",
    ("b", True): "bg-slate-800/40 border-2 border-opponent-chess-available-target-marker",
}
_CHESS_PIECE_Z_INDEXES: dict[str, str] = {
    # N.B. z-indexes must be multiples of 10 in Tailwind.
    "ground_marker": "z-0",
    "symbol": "z-10",
    "character": "z-20",
}


_BOT_MOVE_DELAY = 500  # we'll wait that amount of milliseconds before starting the bot move's calculation
_PLAY_BOT_JS_TEMPLATE = Template(
    """
<script>
    (function () {
        setTimeout(function () {
            window.playBotMove("$FEN", "$PLAY_MOVE_HTMX_ELEMENT_ID", "$BOT_ASSETS_DATA_HOLDER_ELEMENT_ID", $FORCED_MOVE);
        }, $MOVE_DELAY);
    })()</script>"""
)


def chess_arena(*, game_presenter: "GamePresenter", board_id: str) -> dom_tag:
    return div(
        # stats_modal(),
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
        chess_daily_challenge_bar(game_presenter=game_presenter, board_id=board_id),
        chess_status_bar(game_presenter=game_presenter, board_id=board_id),
        id=f"chess-arena-{board_id}",
        cls="w-full md:max-w-xl mx-auto",
        # When the user clicks on anything that is not an interactive element of the chess board, and the state
        # of this chess board is not "waiting_for_player_selection", then the chess board is reset to this state.
        data_hx_get=f"{ reverse('chess:htmx_game_no_selection') }?{ urlencode({'board_id': board_id}) }",
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


@cache
def chess_board_square(square: "Square") -> dom_tag:
    file, rank = file_and_rank_from_square(square)
    square_index = FILE_NAMES.index(file) + RANK_NAMES.index(rank)
    square_color_cls = SQUARE_COLOR_TAILWIND_CLASSES[square_index % 2]
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

    piece_can_be_moved_by_player = (
        game_presenter.is_player_turn and square in game_presenter.squares_with_pieces_that_can_move
    )
    ground_marker = chess_unit_ground_marker(player_side=player_side, can_move=piece_can_be_moved_by_player)
    unit_display = chess_character_display(piece_role=piece_role, game_presenter=game_presenter, square=square)
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

    htmx_attributes = {
        "data_hx_trigger": "click",
        "data_hx_get": f"{reverse('chess:htmx_game_select_piece')}?{urlencode({'square': square, 'board_id': board_id})}",
        "data_hx_target": f"#chess-board-available-targets-{board_id}",
    }

    return div(
        ground_marker,
        unit_display,
        unit_chess_symbol_display,
        cls=" ".join(classes),
        id=f"board-{ board_id }-side-{ player_side }-piece-{ piece_role }",
        **htmx_attributes,
        # These 2 are mostly for debugging purposes:
        data_square=square,
        data_piece_role=piece_role,
    )


def chess_available_targets(*, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str) -> dom_tag:
    children: list[dom_tag] = []

    if game_presenter.selected_piece and not game_presenter.is_game_over:
        selected_piece_player_side = game_presenter.selected_piece.player_side
        for square in game_presenter.selected_piece.available_targets:
            children.append(
                chess_available_target(
                    game_presenter=game_presenter,
                    piece_player_side=selected_piece_player_side,
                    square=square,
                    board_id=board_id,
                )
            )

    return div(
        *children,
        cls="relative aspect-square pointer-events-none",
        id=f"chess-board-available-targets-{board_id}",
        **extra_attrs,
    )


def chess_available_target(
    *, game_presenter: "GamePresenter", piece_player_side: "PlayerSide", square: "Square", board_id: str
) -> dom_tag:
    assert game_presenter.selected_piece is not None
    can_move = not game_presenter.is_game_over and game_presenter.active_player_side == piece_player_side
    bg_class = "bg-active-chess-available-target-marker" if can_move else "bg-opponent-chess-available-target-marker"
    hover_class = "hover:w-1/3 hover:h-1/3" if can_move else ""
    target_marker = div(
        cls=f"w-1/5 h-1/5 rounded-full transition-size {bg_class} {hover_class}",
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
    ]
    if can_move:
        classes += ["cursor-pointer", "pointer-events-auto"]
    else:
        classes += ["pointer-events-none"]

    if can_move:
        htmx_attributes = {
            "data_hx_post": f"{reverse('chess:htmx_game_move_piece', kwargs={'from_': game_presenter.selected_piece.square, 'to': square})}?{urlencode({'board_id': board_id})}",
            "data_hx_target": f"#chess-board-pieces-{ board_id }",
            "data_hx_swap": "outerHTML",
        }
    else:
        htmx_attributes = {}

    return div(
        target_marker_container,
        cls=" ".join(classes),
        **htmx_attributes,
        # This one is mostly for debugging purposes:
        data_square=square,
    )


def chess_character_display(
    *,
    piece_role: "PieceRole",
    game_presenter: "GamePresenter | None" = None,
    square: "Square | None" = None,
    additional_classes: "Sequence[str]|None" = None,
    factions: "Factions | None" = None,
) -> dom_tag:
    assert game_presenter or factions, "You must provide either a GamePresenter or a Factions kwarg."

    # Some data we'll need:
    piece_player_side = player_side_from_piece_role(piece_role)
    is_active_player_piece = game_presenter.active_player == piece_player_side if game_presenter else False
    is_highlighted = bool(
        square and game_presenter and game_presenter.selected_piece and game_presenter.selected_piece.square == square
    )
    is_potential_capture = bool(
        game_presenter and game_presenter.selected_piece and game_presenter.selected_piece.is_potential_capture(square)
    )
    is_w_side = piece_player_side == "w"
    piece_type: "PieceType" = type_from_piece_role(piece_role)
    is_knight, is_king = piece_type == "n", piece_type == "k"

    # Right, let's do this shall we?
    if is_king and is_active_player_piece and game_presenter and game_presenter.is_check:
        is_potential_capture = True  # let's highlight our king if it's in check
    horizontal_translation = (
        ("left-2" if is_w_side else "right-2") if is_knight else ("left-0" if is_w_side else "right-0")
    )
    vertical_translation = "top-1" if is_knight else "top-2"

    game_factions = cast("Factions", factions or game_presenter.factions)  # type: ignore

    classes = [
        "relative",
        "w-11/12",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        _CHESS_PIECE_Z_INDEXES["character"],
        horizontal_translation,
        vertical_translation,
        *piece_character_classes(piece_role=piece_role, factions=game_factions),
        # Conditional classes:
        ("drop-shadow-active-selected-piece" if is_active_player_piece else "drop-shadow-opponent-selected-piece")
        if is_highlighted
        else "",
        "drop-shadow-potential-capture" if is_potential_capture else "",
    ]
    if additional_classes:
        classes.extend(additional_classes)

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
        _CHESS_PIECE_Z_INDEXES["ground_marker"],
        "border-solid",
        _PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES[(player_side, can_move)],
    ]
    return div(
        cls=" ".join(classes),
    )


def chess_unit_display_with_ground_marker(
    *,
    piece_role: "PieceRole",
    game_presenter: "GamePresenter | None" = None,
    factions: "Factions | None" = None,
) -> dom_tag:
    assert game_presenter or factions, "You must provide either a GamePresenter or a Factions kwarg."

    player_side = player_side_from_piece_role(piece_role)

    ground_marker = chess_unit_ground_marker(player_side=player_side)
    unit_display = chess_character_display(piece_role=piece_role, game_presenter=game_presenter, factions=factions)

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

    is_pawn = piece_type == "p"
    is_light_square = square_color == "light"

    symbol_class = (
        "w-7" if is_pawn else "w-8",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        "opacity-60" if is_light_square else "opacity-50",
        "brightness-50",
        chess_unit_symbol_class(player_side="b", piece_name=piece_name),
    )
    symbol_display = div(
        cls=" ".join(symbol_class),
    )

    symbol_display_container_classes = (
        "absolute",
        # We have to do some ad-hoc adjustments for Knights:
        # "-top-1",  # "-top-1" if piece_type == "n" else "top-0",
        "top-0",
        # ("-left-1" if player_side == "w" else "-right-1")
        "left-0" if player_side == "w" else "right-0",
        # if piece_type == "n"
        # else ("right-0" if player_side == "w" else "left-0"),
        _CHESS_PIECE_Z_INDEXES["symbol"],
        # Quick custom display for white knights, so they face the inside of the board:
        "-scale-x-100" if player_side == "w" and piece_type == "n" else "",
    )

    return div(
        symbol_display,
        cls=" ".join(symbol_display_container_classes),
        aria_label=piece_name,
    )


def _bot_turn_html_elements(*, game_presenter: "GamePresenter", board_id: str) -> list[dom_tag]:
    if not game_presenter.is_bot_turn or game_presenter.is_game_over:
        return []

    play_move_htmx_element_id = f"chess-bot-play-move-{ board_id }"
    forced_bot_move = json.dumps("".join(game_presenter.forced_bot_move) if game_presenter.forced_bot_move else None)
    move_delay = _BOT_MOVE_DELAY * 2 if game_presenter.forced_bot_move else _BOT_MOVE_DELAY

    htmx_attributes = {
        "data_hx_post": f"{reverse('chess:htmx_game_bot_move')}?{urlencode({'board_id': board_id, 'move': 'BOT_MOVE'})}",
        "data_hx_target": f"#chess-board-pieces-{board_id}",
        "data_hx_trigger": "playMove",
    }

    return [
        unescaped_html(
            _PLAY_BOT_JS_TEMPLATE.safe_substitute(
                {
                    "FEN": game_presenter.fen,
                    "PLAY_MOVE_HTMX_ELEMENT_ID": play_move_htmx_element_id,
                    "BOT_ASSETS_DATA_HOLDER_ELEMENT_ID": f"chess-bot-data-{ board_id }",
                    "MOVE_DELAY": move_delay,
                    "FORCED_MOVE": forced_bot_move,
                }
            )
        ),
        div(
            id=play_move_htmx_element_id,
            **htmx_attributes,
        ),
    ]

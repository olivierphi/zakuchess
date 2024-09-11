import json
from functools import cache
from string import Template
from typing import TYPE_CHECKING, Literal, cast

from chess import FILE_NAMES, RANK_NAMES
from django.conf import settings
from django.templatetags.static import static
from dominate.tags import button, div, section, span
from dominate.util import raw as unescaped_html

from ..chess_helpers import (
    file_and_rank_from_square,
    piece_name_from_piece_role,
    player_side_from_piece_role,
    type_from_piece_role,
)
from ..models import UserPrefsBoardTexture, UserPrefsGameSpeed
from .chess_helpers import (
    chess_unit_symbol_class,
    piece_character_classes,
    piece_should_face_left,
    square_to_positioning_tailwind_classes,
)
from .misc_ui import speech_bubble_container

if TYPE_CHECKING:
    from collections.abc import Sequence

    from dominate.tags import dom_tag

    from ..models import GameFactions
    from ..presenters import GamePresenter
    from ..types import (
        BoardOrientation,
        PieceRole,
        PieceType,
        PlayerSide,
        Square,
    )


SQUARE_COLOR_TAILWIND_CLASSES = ("bg-chess-square-dark", "bg-chess-square-light")
# SQUARE_COLOR_TAILWIND_CLASSES = ("bg-slate-600", "bg-zinc-400")
# SQUARE_COLOR_TAILWIND_CLASSES = ("bg-orange-600", "bg-orange-400")
INFO_BARS_COMMON_CLASSES = (
    "p-2 text-slate-200 bg-slate-800 border-2 border-solid border-slate-400"
)
_PIECE_GROUND_MARKER_COLOR_TAILWIND_CLASSES: dict[tuple["PlayerSide", bool], str] = {
    # the boolean says if the piece can move
    ("w", False): "bg-emerald-800/40 border-2 border-emerald-800",
    ("b", False): "bg-indigo-800/40 border-2 border-indigo-800",
    ("w", True): "bg-emerald-600/40 border-2 border-emerald-800",
    ("b", True): "bg-indigo-600/40 border-2 border-indigo-800",
}
_CHESS_PIECE_Z_INDEXES: dict[str, str] = {
    # N.B. z-indexes must be multiples of 10 in Tailwind.
    "ground_marker": "z-0",
    "symbol": "z-10",
    "character": "z-20",
}

# TODO: get rid of _PLAY_BOT_JS_TEMPLATE and _PLAY_SOLUTION_JS_TEMPLATE, and implement
#   this as Web Components we return in the HTMX response.
# We'll wait that amount of milliseconds before starting the bot move's calculation:
_BOT_MOVE_DELAY = 700
_BOT_MOVE_DELAY_FIRST_TURN_OF_THE_DAY = 1_400
_BOT_MOVE_DELAY_FAST_MODE = 100
_PLAY_BOT_JS_TEMPLATE = Template(
    """
<script>
    (function () {
        setTimeout(function () {
            window.playBotMove({
                fen: "${FEN}",
                htmxElementId: "${PLAY_MOVE_HTMX_ELEMENT_ID}",
                botAssetsDataHolderElementId: "${BOT_ASSETS_DATA_HOLDER_ELEMENT_ID}",
                forcedMove: ${FORCED_MOVE},
                depth: ${DEPTH},
            });
        }, ${MOVE_DELAY});
    })()</script>"""
)

_PLAY_SOLUTION_MOVE_DELAY = 1200
_PLAY_SOLUTION_JS_TEMPLATE = Template(
    """
<script>
    (function () {
        setTimeout(
            htmx.trigger.bind(null, "${PLAY_MOVE_HTMX_ELEMENT_SELECTOR}", "playSolutionNextMove", {}),
            ${MOVE_DELAY}
        );
    })()</script>"""
)


def chess_arena(
    *, game_presenter: "GamePresenter", status_bars: "list[dom_tag]", board_id: str
) -> "dom_tag":
    arena_additional_classes = (
        "border-3 border-solid md:border-lime-400 xl:border-red-400"
        if settings.DEBUG_LAYOUT
        else ""
    )

    return section(
        div(
            div(
                div(
                    chess_board(game_presenter=game_presenter, board_id=board_id),
                    cls="absolute inset-0 pointer-events-none z-0",
                    id=f"chess-board-container-{board_id}",
                ),
                div(
                    chess_last_move(game_presenter=game_presenter, board_id=board_id),
                    cls="absolute inset-0 pointer-events-none z-10",
                    id=f"chess-last-move-container-{board_id}",
                ),
                div(
                    chess_pieces(game_presenter=game_presenter, board_id=board_id),
                    cls="absolute inset-0 pointer-events-none z-20",
                    id=f"chess-pieces-container-{board_id}",
                ),
                div(
                    chess_available_targets(
                        game_presenter=game_presenter, board_id=board_id
                    ),
                    cls="absolute inset-0 pointer-events-none z-30",
                    id=f"chess-available-targets-container-{board_id}",
                ),
                div(
                    speech_bubble_container(
                        game_presenter=game_presenter, board_id=board_id
                    ),
                    cls="absolute inset-0 pointer-events-none z-40",
                    id=f"chess-speech-container-{board_id}",
                ),
                cls="aspect-square relative mx-auto max-w-[calc(100dvh-80px)]",
            ),
            id=f"chess-board-components-{board_id}",
            cls="xl:w-2/3 bg-slate-800",
        ),
        chess_bot_data(board_id),
        div(
            *status_bars,
            id=f"chess-status-bars-{board_id}",
            cls="xl:px-2 xl:w-1/3 xl:bg-slate-950",
        ),
        id=f"chess-arena-{board_id}",
        cls="w-full mx-auto bg-slate-900 "
        f"md:max-w-3xl xl:max-w-7xl xl:flex xl:border xl:rounded-md xl:border-neutral-800 {arena_additional_classes}",
        # When the user clicks on anything that is not an interactive element
        # of the chess board, and the state of this chess board is not
        # "waiting_for_player_selection", then the chess board is reset to this state.
        data_hx_get=game_presenter.urls.htmx_game_no_selection_url(board_id=board_id),
        data_hx_trigger=f"click[cursorIsNotOnChessBoardInteractiveElement('{ board_id }')] from:document",
        data_hx_target=f"#chess-board-pieces-{ board_id }",
    )


def chess_bot_data(board_id: str) -> "dom_tag":
    # This is used in "chess-bot.ts"
    match settings.JS_CHESS_ENGINE.lower():
        case "lozza":
            chess_engine_urls = {
                "id": "lozza",
                "js": static("chess/js/bot/lozza.js"),
            }
        case "stockfish" | _:
            chess_engine_urls = {
                "id": "stockfish",
                "wasm": static("chess/js/bot/stockfish.wasm.js"),
                "js": static("chess/js/bot/stockfish.js"),
            }

    return div(
        id=f"chess-bot-data-{board_id}",
        aria_hidden="true",
        data_chess_engine_urls=json.dumps(chess_engine_urls),
    )


def chess_board(*, game_presenter: "GamePresenter", board_id: str) -> "dom_tag":
    force_square_info: bool = (
        game_presenter.force_square_info or game_presenter.is_preview
    )
    squares: list[dom_tag] = []
    match game_presenter.board_orientation:
        case "1->8":
            for file in FILE_NAMES:
                for rank in RANK_NAMES:
                    squares.append(
                        chess_board_square(
                            game_presenter.board_orientation,
                            cast("Square", f"{file}{rank}"),
                            force_square_info=force_square_info,
                        )
                    )
        case "8->1":
            for file in reversed(FILE_NAMES):
                for rank in reversed(RANK_NAMES):
                    squares.append(
                        chess_board_square(
                            game_presenter.board_orientation,
                            cast("Square", f"{file}{rank}"),
                            force_square_info=force_square_info,
                        )
                    )

    squares_container_classes: list[str] = [
        "relative",
        "aspect-square",
    ]
    chess_board_additional_attributes: dict[str, str] = {}

    # That's where we manage the optional texture we apply to the chess board:
    match game_presenter.user_prefs.board_texture:
        case UserPrefsBoardTexture.ABSTRACT:
            squares_container_classes.append("opacity-85")
            chess_board_additional_attributes["style"] = (
                f"background: url('{ static('chess/img/board/texture.jpg') }') repeat"
            )
        case _:
            pass

    squares_container = div(
        *squares,
        id=f"chess-board-squares-{board_id}",
        cls=" ".join(squares_container_classes),
    )

    return div(
        squares_container,
        id=f"chess-board-{board_id}",
        cls="pointer-events-none",
        **chess_board_additional_attributes,
    )


def chess_pieces(
    *, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str
) -> "dom_tag":
    pieces_to_append: "list[tuple[Square, PieceRole]]" = sorted(
        # We sort the pieces by their role, so that the pieces are always displayed
        # in the same order, regardless of their position on the chess board.
        game_presenter.piece_role_by_square.items(),
        key=lambda item: item[1],
    )

    pieces: "list[dom_tag]" = []
    for square, piece_role in pieces_to_append:
        pieces.append(
            chess_piece(
                square=square,
                piece_role=piece_role,
                game_presenter=game_presenter,
                board_id=board_id,
            )
        )

    bot_turn_html_elements = _bot_turn_html_elements(
        game_presenter=game_presenter, board_id=board_id
    )
    solution_play_html_elements = _solution_turn_html_elements(
        game_presenter=game_presenter, board_id=board_id
    )

    return div(
        div(
            data_board_state=game_presenter.game_phase,
            aria_hidden="true",
        ),
        *pieces,
        *bot_turn_html_elements,
        *solution_play_html_elements,
        id=f"chess-board-pieces-{board_id}",
        cls="relative aspect-square",
        **extra_attrs,
    )


@cache
def chess_board_square(
    board_orientation: "BoardOrientation",
    square: "Square",
    *,
    force_square_info: bool = False,
) -> "dom_tag":
    file, rank = file_and_rank_from_square(square)
    square_index = FILE_NAMES.index(file) + RANK_NAMES.index(rank)
    square_color_cls = SQUARE_COLOR_TAILWIND_CLASSES[square_index % 2]
    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        square_color_cls,
        *square_to_positioning_tailwind_classes(board_orientation, square),
    ]

    displayed_file, displayed_rank = None, None
    if force_square_info:
        displayed_file, displayed_rank = file, rank
    else:
        match board_orientation:
            case "1->8":
                if rank == "1":
                    displayed_file = file
                if file == "a":
                    displayed_rank = rank
            case "8->1":
                if rank == "8":
                    displayed_file = file
                if file == "h":
                    displayed_rank = rank
    if displayed_file or displayed_rank:
        square_name = f"{displayed_file or ''}{displayed_rank or ''}"
        square_info = span(
            square_name,
            cls="text-chess-square-square-info select-none",
        )
    else:
        square_info = ""

    return div(
        square_info,
        cls=" ".join(classes),
        # Mostly for debugging purposes:
        data_square=square,
    )


def chess_piece(
    *,
    game_presenter: "GamePresenter",
    square: "Square",
    piece_role: "PieceRole",
    board_id: str,
) -> "dom_tag":
    player_side = player_side_from_piece_role(piece_role)

    piece_can_be_moved_by_player = (
        game_presenter.solution_index is not None
        and game_presenter.is_my_turn
        and square in game_presenter.squares_with_pieces_that_can_move
    )
    unit_display = chess_character_display(
        piece_role=piece_role, game_presenter=game_presenter, square=square
    )
    unit_chess_symbol_display = chess_unit_symbol_display(
        board_orientation=game_presenter.board_orientation, piece_role=piece_role
    )
    ground_marker = chess_unit_ground_marker(
        player_side=player_side, can_move=piece_can_be_moved_by_player
    )
    is_selected_piece = bool(
        square
        and game_presenter.selected_piece
        and game_presenter.selected_piece.square == square
    )
    is_game_over = game_presenter.is_game_over

    animation_speed = (
        "duration-300"
        if game_presenter.user_prefs.game_speed == UserPrefsGameSpeed.NORMAL
        else "duration-75"  # almost instant
    )
    classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        *square_to_positioning_tailwind_classes(
            game_presenter.board_orientation, square
        ),
        "cursor-pointer" if not is_game_over else "cursor-default",
        "pointer-events-auto" if not is_game_over else "pointer-events-none",
        # Transition-related classes:
        "transition-coordinates",
        animation_speed,
        "ease-in",
        "transform-gpu",
    ]

    additional_attributes: dict = {}
    htmx_attributes: dict[str, str] = {}
    if not is_game_over and game_presenter.can_select_pieces:
        htmx_attributes = {
            "data_hx_trigger": "click",
            "data_hx_get": (
                game_presenter.urls.htmx_game_select_piece_url(
                    square=square,
                    board_id=board_id,
                )
                if not is_selected_piece
                # Re-selecting an already selected piece de-selects it:
                else game_presenter.urls.htmx_game_no_selection_url(board_id=board_id)
            ),
            "data_hx_target": f"#chess-pieces-container-{board_id}",
        }
    else:
        additional_attributes["disabled"] = True

    return button(
        ground_marker,
        unit_display,
        unit_chess_symbol_display,
        cls=" ".join(classes),
        id=f"board-{ board_id }-side-{ player_side }-piece-{ piece_role }",
        **htmx_attributes,
        **additional_attributes,
        # These 2 are mostly for debugging purposes:
        data_square=square,
        data_piece_role=piece_role,
    )


def chess_available_targets(
    *, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str
) -> "dom_tag":
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
    *,
    game_presenter: "GamePresenter",
    piece_player_side: "PlayerSide",
    square: "Square",
    board_id: str,
) -> "dom_tag":
    assert game_presenter.selected_piece is not None
    can_move = (
        not game_presenter.is_game_over
        and game_presenter.is_my_turn
        and game_presenter.active_player_side == piece_player_side
    )
    bg_class = (
        "bg-active-chess-available-target-marker"
        if can_move
        else "bg-opponent-chess-available-target-marker"
    )
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
        "block",
        *square_to_positioning_tailwind_classes(
            game_presenter.board_orientation, square
        ),
    ]
    additional_attributes = {}

    if can_move:
        classes += ["cursor-pointer", "pointer-events-auto"]
    else:
        classes += ["pointer-events-none"]
        additional_attributes["disabled"] = True

    if can_move:
        htmx_attributes = {
            "data_hx_post": game_presenter.urls.htmx_game_move_piece_url(
                square=square, board_id=board_id
            ),
            "data_hx_target": f"#chess-pieces-container-{board_id}",
        }
    else:
        htmx_attributes = {}

    return button(
        target_marker_container,
        cls=" ".join(classes),
        **htmx_attributes,
        **additional_attributes,
        # Mostly for debugging purposes:
        data_square=square,
    )


def chess_character_display(
    *,
    piece_role: "PieceRole",
    game_presenter: "GamePresenter | None" = None,
    square: "Square | None" = None,
    additional_classes: "Sequence[str]|None" = None,
    factions: "GameFactions | None" = None,
    board_orientation: "BoardOrientation" = "1->8",
) -> "dom_tag":
    assert (
        game_presenter or factions
    ), "You must provide either a GamePresenter or a Factions kwarg."

    # Some data we'll need:
    piece_player_side = player_side_from_piece_role(piece_role)
    is_active_player_piece = (
        game_presenter.active_player == piece_player_side if game_presenter else False
    )
    is_potential_capture: bool = False
    is_highlighted: bool = False
    if square and game_presenter and game_presenter.solution_index is None:
        if (
            game_presenter.selected_piece
            and game_presenter.selected_piece.square == square
        ):
            is_highlighted = True
        elif (
            game_presenter.player_side_to_highlight_all_pieces_for == piece_player_side
        ):
            is_highlighted = True

        if (
            game_presenter.selected_piece
            and game_presenter.selected_piece.is_potential_capture(square)
        ):
            is_potential_capture = True

    if game_presenter:
        board_orientation = game_presenter.board_orientation
    is_from_original_left_hand_side = (
        piece_player_side == "w"
        if board_orientation == "1->8"
        else piece_player_side == "b"
    )
    piece_type: "PieceType" = type_from_piece_role(piece_role)
    is_knight, is_king = piece_type == "n", piece_type == "k"

    # Right, let's do this shall we?
    if (
        is_king
        and is_active_player_piece
        and game_presenter
        and game_presenter.solution_index is None
        and game_presenter.is_check
    ):
        is_potential_capture = True  # let's highlight our king if it's in check
    elif (
        is_king
        and is_active_player_piece
        and game_presenter
        and game_presenter.solution_index is not None
        and game_presenter.is_check
    ):
        is_potential_capture = True  # let's highlight checks in "see solution" mode

    horizontal_translation = (
        ("left-3" if is_knight else "left-0")
        if is_from_original_left_hand_side
        else "right-0"
    )
    vertical_translation = (
        "top-2" if is_knight and is_from_original_left_hand_side else "top-1"
    )

    game_factions = cast("GameFactions", factions or game_presenter.factions)  # type: ignore

    classes = [
        "relative",
        "w-10/12" if is_knight else "w-11/12",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        _CHESS_PIECE_Z_INDEXES["character"],
        horizontal_translation,
        vertical_translation,
        *piece_character_classes(
            board_orientation=board_orientation,
            piece_role=piece_role,
            factions=game_factions,
        ),
        # Conditional classes:
        (
            (
                "drop-shadow-active-selected-piece"
                if is_active_player_piece
                else "drop-shadow-opponent-selected-piece"
            )
            if is_highlighted
            else (
                "drop-shadow-piece-symbol-w"
                if piece_player_side == "w"
                else "drop-shadow-piece-symbol-b"
            )
        ),
        "drop-shadow-potential-capture" if is_potential_capture else "",
    ]
    if additional_classes:
        classes.extend(additional_classes)

    return div(
        cls=" ".join(classes),
        data_piece_role=piece_role,
    )


def chess_unit_ground_marker(
    *, player_side: "PlayerSide", can_move: bool = False
) -> "dom_tag":
    classes = [
        "absolute",
        "w-11/12",
        "h-2/5",
        "left-1/24",
        "bottom-0.5",
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
    factions: "GameFactions | None" = None,
) -> "dom_tag":
    assert (
        game_presenter or factions
    ), "You must provide either a GamePresenter or a Factions kwarg."

    player_side = player_side_from_piece_role(piece_role)

    ground_marker = chess_unit_ground_marker(player_side=player_side)
    unit_display = chess_character_display(
        piece_role=piece_role, game_presenter=game_presenter, factions=factions
    )

    return div(
        ground_marker,
        unit_display,
        cls="relative h-full aspect-square",
    )


def chess_unit_symbol_display(
    *, board_orientation: "BoardOrientation", piece_role: "PieceRole"
) -> "dom_tag":
    player_side = player_side_from_piece_role(piece_role)
    piece_type = type_from_piece_role(piece_role)
    piece_name = piece_name_from_piece_role(piece_role)

    is_knight, is_pawn = piece_type == "n", piece_type == "p"

    symbol_class = (
        # We have to do some ad-hoc adjustments for Knights and Pawns:
        "w-7" if (is_pawn or is_knight) else "w-8",
        "aspect-square",
        "bg-no-repeat",
        "bg-cover",
        "opacity-90",
        (
            "drop-shadow-piece-symbol-w"
            if player_side == "w"
            else "drop-shadow-piece-symbol-b"
        ),
        chess_unit_symbol_class(player_side=player_side, piece_name=piece_name),
    )
    symbol_display = div(
        cls=" ".join(symbol_class),
    )

    should_face_left = piece_should_face_left(board_orientation, player_side)
    symbol_display_container_classes = (
        "absolute",
        "top-0",
        "right-0" if should_face_left else "left-0",
        _CHESS_PIECE_Z_INDEXES["symbol"],
        # Quick custom display for white knights, so they face the inside of the board:
        "-scale-x-100" if is_knight and not should_face_left else "",
    )

    return div(
        symbol_display,
        cls=" ".join(symbol_display_container_classes),
        data_label=piece_name,
    )


def chess_last_move(
    *, game_presenter: "GamePresenter", board_id: str, **extra_attrs: str
) -> "dom_tag":
    children: list[dom_tag] = []
    if last_move := game_presenter.last_move:
        children.extend(
            [
                chess_last_move_marker(
                    board_orientation=game_presenter.board_orientation,
                    square=last_move[0],
                    move_part="from",
                ),
                chess_last_move_marker(
                    board_orientation=game_presenter.board_orientation,
                    square=last_move[1],
                    move_part="to",
                ),
            ]
        )

    return div(
        *children,
        cls="relative aspect-square pointer-events-none",
        id=f"chess-last-move-{board_id}",
        **extra_attrs,
        # Mostly for debugging purposes:
        data_last_move=str(last_move or ""),
    )


def chess_last_move_marker(
    *,
    board_orientation: "BoardOrientation",
    square: "Square",
    move_part: Literal["from", "to"],
) -> "dom_tag":
    match move_part:
        case "from":
            start_class = "!w-full"
            target_class = "w-3/5"
        case "to":
            start_class = "!w-3/5"
            target_class = "w-11/12"
        case _:
            raise ValueError(f"Invalid move_part: { move_part }")

    movement_marker_classes = (
        "aspect-square",
        "bg-sky-300",
        "opacity-70",
        "border",
        "border-sky-500",
        "rounded-full",
        "transition-size",
        "duration-400",
        "ease-in-out",
        "transform-gpu",
        start_class,
        target_class,
    )

    movement_marker = div(
        "",
        cls=" ".join(movement_marker_classes),
        data_classes=f"remove {start_class}",
        # Mostly for debugging purposes:
        data_last_move_marker=move_part,
    )

    movement_marker_container_classes = [
        "absolute",
        "aspect-square",
        "w-1/8",
        "flex items-center justify-center",
        *square_to_positioning_tailwind_classes(board_orientation, square),
    ]

    return div(
        movement_marker,
        cls=" ".join(movement_marker_container_classes),
    )


def _bot_turn_html_elements(
    *, game_presenter: "GamePresenter", board_id: str
) -> "list[dom_tag]":
    if (
        game_presenter.solution_index is not None
        or not game_presenter.is_bot_turn
        or game_presenter.is_game_over
    ):
        return []

    play_move_htmx_element_id = f"chess-bot-play-move-{ board_id }"
    forced_bot_move = json.dumps(game_presenter.forced_bot_move or None)

    if game_presenter.forced_bot_move:
        move_delay = _BOT_MOVE_DELAY_FIRST_TURN_OF_THE_DAY
    elif game_presenter.user_prefs.game_speed == UserPrefsGameSpeed.FAST:
        move_delay = _BOT_MOVE_DELAY_FAST_MODE
    else:
        move_delay = _BOT_MOVE_DELAY

    htmx_attributes = {
        "data_hx_post": game_presenter.urls.htmx_game_play_bot_move_url(
            board_id=board_id
        ),
        "data_hx_target": f"#chess-pieces-container-{board_id}",
        "data_hx_trigger": "playMove",
    }
    bot_move_script_tag = unescaped_html(
        _PLAY_BOT_JS_TEMPLATE.safe_substitute(
            {
                "FEN": game_presenter.fen,
                "PLAY_MOVE_HTMX_ELEMENT_ID": play_move_htmx_element_id,
                "BOT_ASSETS_DATA_HOLDER_ELEMENT_ID": f"chess-bot-data-{ board_id }",
                "FORCED_MOVE": forced_bot_move,
                "DEPTH": game_presenter.bot_depth,
                "MOVE_DELAY": move_delay,
            }
        )
    )

    return [
        bot_move_script_tag,
        div(
            id=play_move_htmx_element_id,
            **htmx_attributes,
        ),
    ]


def _solution_turn_html_elements(
    *, game_presenter: "GamePresenter", board_id: str
) -> "list[dom_tag]":
    if game_presenter.solution_index is None or game_presenter.is_game_over:
        return []

    play_move_htmx_element_id = f"chess-solution-play-half-move-{board_id}"

    htmx_attributes = {
        "data_hx_post": game_presenter.urls.htmx_game_play_solution_move_url(
            board_id=board_id
        ),
        "data_hx_target": f"#chess-pieces-container-{board_id}",
        "data_hx_trigger": "playSolutionNextMove",
    }

    bot_move_script_tag = unescaped_html(
        _PLAY_SOLUTION_JS_TEMPLATE.safe_substitute(
            {
                "PLAY_MOVE_HTMX_ELEMENT_SELECTOR": f"#{play_move_htmx_element_id}",
                "MOVE_DELAY": _PLAY_SOLUTION_MOVE_DELAY,
            }
        )
    )

    return [
        bot_move_script_tag,
        div(
            id=play_move_htmx_element_id,
            **htmx_attributes,
        ),
    ]

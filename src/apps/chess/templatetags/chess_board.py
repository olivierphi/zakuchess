from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django import template
from django.utils.safestring import mark_safe

from apps.chess.chess_helpers import chess_lib_color_to_player_side
from apps.chess.consts import FILES, RANKS
from apps.daily_challenge.consts import FACTIONS

if TYPE_CHECKING:
    import chess
    from django.utils.safestring import SafeString

    from apps.chess.game_state import GameState
    from apps.chess.types import BoardOrientation, File, Rank, Square

register = template.Library()

_logger = logging.getLogger(__name__)


@register.simple_tag()
def chess_board_squares(game_state: GameState) -> SafeString:
    squares: list[str] = []
    for file in FILES:
        for rank in RANKS:
            square_info = _get_square_info(file, rank, game_state.board_orientation)
            squares.append(
                f"""<div data-square="{file}{rank}">{square_info or ""}</div>"""
            )
    return mark_safe("\n".join(squares))


@register.simple_tag()
def chess_board_pieces(game_state: GameState) -> SafeString:
    pieces: list[str] = []
    # TODO: move some of this to the game state
    legal_moves = game_state.legal_moves
    squares_with_pieces_that_can_move = {move[0] for move in legal_moves}

    for square, piece in game_state.pieces.items():
        piece = chess_board_piece(
            game_state, square, piece, squares_with_pieces_that_can_move
        )
        pieces.append(piece)

    return mark_safe("\n".join(pieces))


def chess_board_piece(
    game_state: GameState,
    square: Square,
    piece: chess.Piece,
    squares_with_pieces_that_can_move: set[Square],
) -> SafeString:
    player_side = chess_lib_color_to_player_side(piece.color)
    character_faction = getattr(FACTIONS, player_side)
    can_move = square in squares_with_pieces_that_can_move
    character_data = game_state.get_character_at(square)

    marker_element = f"<div {
        ' '.join(
            f'{attr}="{value}"'
            for attr, value in {
                'class': 'chess-marker',
                'data-faction': character_faction,
                # **({"data-can-move": "1"} if can_move else {}),
            }.items()
        )
    }></div>"

    symbol_element = f"<div {
        ' '.join(
            f'{attr}="{value}"'
            for attr, value in {
                'class': 'chess-symbol',
                'data-player-side': player_side,
                'data-symbol': piece.symbol(),
                'data-faction': character_faction,
            }.items()
        )
    }></div>"

    character_element = f"<div {
        ' '.join(
            f'{attr}="{value}"'
            for attr, value in {
                'class': 'chess-character',
                'data-player-side': player_side,
                'data-symbol': piece.symbol().lower(),
                'data-faction': character_faction,
                # Just a temporary test to check that we can find the right character
                # for each chess piece we display:
                'data-name': ' '.join(character_data.get('name', [])),
            }.items()
        )
    }></div>"

    tag = "button" if can_move else "div"
    tag_id = f"piece-{game_state.board_id}-{player_side}-{character_data['id']}"
    piece_element = f"""
        <{tag} id="{tag_id}" class="chess-piece" data-square="{square}">
            {marker_element}
            {'"<div class="chess-marker-can-move"></div>"' if can_move else ""}
            {symbol_element}
            {character_element}
        </{tag}>
    """

    return mark_safe(piece_element)


def _get_square_info(
    file: File, rank: Rank, board_orientation: BoardOrientation
) -> str | None:
    displayed_file, displayed_rank = None, None

    match board_orientation:
        case "1-to-8":
            if file == "a":
                displayed_rank = rank
            if rank == "1":
                displayed_file = file
        case "8-to-1":
            if file == "h":
                displayed_rank = rank
            if rank == "8":
                displayed_file = file

    if displayed_file or displayed_rank:
        square_name = f"{displayed_file or ''}{displayed_rank or ''}"
        return f'<span class="square-info">{square_name}</span>'

    return None

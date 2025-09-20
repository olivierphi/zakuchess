from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django import template
from django.utils.safestring import mark_safe

from apps.chess.business_logic import FILES, RANKS

if TYPE_CHECKING:
    from django.utils.safestring import SafeString

    from apps.chess.business_logic import BoardOrientation, File, Rank
    from apps.chess.game_state import GameState

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
    legal_moves = game_state.legal_moves
    # TODO: move this to the game state
    squares_with_pieces_that_can_move = {move[0] for move in legal_moves}

    for square, piece in game_state.pieces.items():
        # TODO: move this to the game state
        player_side = "w" if piece.color else "b"
        character_faction = "human" if piece.color else "undead"
        can_move = square in squares_with_pieces_that_can_move

        marker = f"<div {
            ' '.join(
                f'{attr}="{value}"'
                for attr, value in {
                    'class': 'chess-marker',
                    'data-faction': character_faction,
                    # **({"data-can-move": "1"} if can_move else {}),
                }.items()
            )
        }></div>"

        symbol = f"<div {
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

        character = f"<div {
            ' '.join(
                f'{attr}="{value}"'
                for attr, value in {
                    'class': 'chess-character',
                    'data-player-side': player_side,
                    'data-symbol': piece.symbol().lower(),
                    'data-faction': character_faction,
                }.items()
            )
        }></div>"

        tag = "button" if can_move else "div"
        pieces.append(f"""
            <{tag} id="piece-{game_state.id}-{piece.symbol()}" class="chess-piece" data-square="{square}">
                {marker}
                {'"<div class="chess-marker-can-move"></div>"' if can_move else ""}
                {symbol}
                {character}
            </{tag}>
        """)
    return mark_safe("\n".join(pieces))


def _get_square_info(
    file: "File", rank: Rank, board_orientation: BoardOrientation
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

from __future__ import annotations

import random
from typing import TYPE_CHECKING, TypeAlias

import chess

from apps.chess.business_logic import calculate_fen_before_move
from apps.chess.chess_helpers import (
    chess_lib_color_to_player_side,
    chess_lib_piece_to_piece_type,
    chess_lib_square_to_square,
    player_side_other,
    uci_to_move,
)
from apps.chess.models import GameTeams
from apps.chess.types import Character

from ..chess.data.character_names import FIRST_NAMES, LAST_NAMES
from .consts import BOT_SIDE

if TYPE_CHECKING:
    from apps.chess.types import (
        FEN,
        CharacterIdBySquare,
        PieceType,
        PlayerSide,
    )

    from .models import DailyChallenge


def compute_fields_before_bot_first_move(
    challenge: DailyChallenge,
) -> None:
    """
    Set the `*_before_bot_first_move` fields on the given challenge models,
    from the value of the other fields.
    """
    # A published challenge always has a `bot_first_move` & `character_id_by_square`:
    assert challenge.bot_first_move and challenge.character_id_by_square

    # Set the `fen_before_bot_first_move` field:
    challenge.fen_before_bot_first_move = calculate_fen_before_move(
        fen_after_move=challenge.fen,
        move=uci_to_move(challenge.bot_first_move),
        moving_player_side=BOT_SIDE,
    )

    # Set the `character_id_by_square_before_bot_first_move` field:
    bot_from, bot_to = uci_to_move(challenge.bot_first_move)
    character_id_by_square = challenge.character_id_by_square.copy()
    character_id_by_square[bot_from] = character_id_by_square[bot_to]
    del character_id_by_square[bot_to]
    challenge.character_id_by_square_before_bot_first_move = character_id_by_square


_TeamsDict: TypeAlias = "dict[PlayerSide, list[Character]]"


def init_daily_challenge_teams(
    *,
    fen: FEN,
    bot_side: PlayerSide = "b",
) -> tuple[GameTeams, CharacterIdBySquare]:
    chess_board = chess.Board(fen)

    # fmt: off
    character_id_counters: dict[PlayerSide, dict[PieceType,int|None]] = {
        "w": {
            "p": 1, "n": 1, "b": 1, "r": 1, "q": None, "k": None
        },
        "b": {
            "p": 1, "n": 1, "b": 1, "r": 1, "q": None, "k": None
        },
    }
    # fmt: on

    character_id_by_square: CharacterIdBySquare = {}

    teams: _TeamsDict = {"w": [], "b": []}

    for chess_square, chess_piece in chess_board.piece_map().items():
        piece_player_side = chess_lib_color_to_player_side(chess_piece.color)
        piece_type = chess_lib_piece_to_piece_type(chess_piece.piece_type)

        character_id_counter = character_id_counters[piece_player_side][piece_type]
        if isinstance(character_id_counter, int):
            character_id = f"{piece_type}{character_id_counter}"
            character_id_counters[piece_player_side][piece_type] += 1  # type: ignore[operator]
        else:
            character_id = piece_type

        square = chess_lib_square_to_square(chess_square)
        character_id_by_square[square] = character_id

        character = Character(
            id=character_id,
            type=piece_type,
            # the name will be managed by `_set_character_names_for_team` below
        )
        teams[piece_player_side].append(character)

    # Give a name to the player's team members
    player_side = player_side_other(bot_side)
    _set_character_names_for_team(teams, player_side)

    return (
        GameTeams(w=tuple(teams["w"]), b=tuple(teams["b"])),
        character_id_by_square,
    )


def _set_character_names_for_team(teams: _TeamsDict, side: PlayerSide) -> None:
    target_characters: list[Character] = teams[side]
    first_names = random.sample(FIRST_NAMES, k=len(target_characters))
    last_names = random.sample(LAST_NAMES, k=len(target_characters))

    for character in target_characters:
        character["name"] = (first_names.pop(), last_names.pop())

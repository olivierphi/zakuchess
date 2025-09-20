from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import chess

from .chess_helpers import chess_lib_color_to_player_side, chess_lib_square_to_square

if TYPE_CHECKING:
    from .types import (
        FEN,
        BoardOrientation,
        Character,
        CharacterId,
        CharacterIdBySquare,
        GameTeamsDict,
        Move,
        PlayerSide,
        Square,
    )


class GameState:
    def __init__(
        self,
        fen: FEN,
        *,
        character_id_by_square: CharacterIdBySquare,
        teams: GameTeamsDict,
        board_orientation: BoardOrientation,
        board_id: str = "main",
    ):
        self._chess = chess.Board(fen)
        self.character_id_by_square = character_id_by_square
        self.teams = teams
        self.board_orientation = board_orientation
        self.board_id = board_id

    @cached_property
    def pieces(self) -> dict[Square, chess.Piece]:
        # TODO: improve this
        return {
            chess_lib_square_to_square(square): piece
            for square, piece in self._chess.piece_map().items()
        }

    @cached_property
    def legal_moves(self) -> tuple[Move, ...]:
        # TODO: improve this
        return tuple(
            (
                chess_lib_square_to_square(move.from_square),
                chess_lib_square_to_square(move.to_square),
            )
            for move in self._chess.legal_moves
        )

    def get_character_at(self, square: Square) -> Character:
        chess_lib_piece = self.pieces[square]
        square_player_side = chess_lib_color_to_player_side(chess_lib_piece.color)

        character_id = self.character_id_by_square[square]
        character = self._characters_by_id[square_player_side][character_id]

        return character

    @cached_property
    def _characters_by_id(self) -> dict[PlayerSide, dict[CharacterId, Character]]:
        return {
            "w": {character["id"]: character for character in self.teams["w"]},
            "b": {character["id"]: character for character in self.teams["b"]},
        }

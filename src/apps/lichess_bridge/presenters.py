from functools import cached_property
from typing import TYPE_CHECKING, cast
from urllib.parse import urlencode

import chess
import chess.pgn
from django.urls import reverse

from apps.chess.presenters import GamePresenter, GamePresenterUrls

from ..chess.chess_helpers import (
    chess_lib_color_to_player_side,
    chess_lib_square_to_square,
    team_member_role_from_piece_role,
)

if TYPE_CHECKING:
    from apps.chess.presenters import SpeechBubbleData
    from apps.chess.types import (
        FEN,
        Factions,
        GamePhase,
        GameTeams,
        PieceRole,
        PieceRoleBySquare,
        PieceSymbol,
        PlayerSide,
        Square,
        TeamMember,
    )

    from .models import LichessGameExportWithMetadata


class LichessCorrespondenceGamePresenter(GamePresenter):
    def __init__(
        self,
        *,
        game_data: "LichessGameExportWithMetadata",
        refresh_last_move: bool,
        is_htmx_request: bool,
        selected_piece_square: "Square | None" = None,
        last_move: tuple["Square", "Square"] | None = None,
    ):
        self._game_data = game_data

        self._chess_board = game_data.chess_board
        fen = cast("FEN", self._chess_board.fen())

        teams, piece_role_by_square = self._create_teams_and_piece_role_by_square(
            self._chess_board, self.factions
        )

        super().__init__(
            fen=fen,
            piece_role_by_square=piece_role_by_square,
            teams=teams,
            refresh_last_move=refresh_last_move,
            is_htmx_request=is_htmx_request,
            selected_piece_square=selected_piece_square,
            last_move=last_move,
        )

    @cached_property
    def urls(self) -> "GamePresenterUrls":
        return LichessCorrespondenceGamePresenterUrls(game_presenter=self)

    @cached_property
    def is_my_turn(self) -> bool:
        return True  # TODO

    @cached_property
    def game_phase(self) -> "GamePhase":
        return "waiting_for_player_selection"  # TODO

    @cached_property
    def is_player_turn(self) -> bool:
        return True  # TODO

    @cached_property
    def is_bot_turn(self) -> bool:
        return False

    @property
    def solution_index(self) -> int | None:
        return None

    @cached_property
    def game_id(self) -> str:
        return self._game_data.game_export.id

    @cached_property
    def factions(self) -> "Factions":
        players = self._game_data.players_from_my_perspective

        return {
            players.me.player_side: "humans",
            players.them.player_side: "undeads",
        }

    @property
    def is_intro_turn(self) -> bool:
        return False

    @cached_property
    def player_side_to_highlight_all_pieces_for(self) -> "PlayerSide | None":
        return None

    @cached_property
    def speech_bubble(self) -> "SpeechBubbleData | None":
        return None

    @staticmethod
    def _create_teams_and_piece_role_by_square(
        chess_board: "chess.Board", factions: "Factions"
    ) -> "tuple[GameTeams, PieceRoleBySquare]":
        # fmt: off
        piece_counters:dict["PieceSymbol", int | None] = {
            "P": 0, "R": 0, "N": 0, "B": 0, "Q": None, "K": None,
            "p": 0, "r": 0, "n": 0, "b": 0, "q": None, "k": None,
        }
        # fmt: on

        teams: "GameTeams" = {"w": [], "b": []}
        piece_role_by_square: "PieceRoleBySquare" = {}
        for chess_square in chess.SQUARES:
            piece = chess_board.piece_at(chess_square)
            if not piece:
                continue

            player_side = chess_lib_color_to_player_side(piece.color)
            symbol = cast("PieceSymbol", piece.symbol())  # e.g. "P", "p", "R", "r"...

            if piece_counters[symbol] is not None:
                piece_counters[symbol] += 1  # type: ignore[operator]
                piece_role = cast(
                    "PieceRole", f"{symbol}{piece_counters[symbol]}"
                )  # e.g "P1", "r2"....
            else:
                piece_role = cast("PieceRole", symbol)  # e.g. "Q", "k"...

            team_member_role = team_member_role_from_piece_role(piece_role)
            team_member: "TeamMember" = {
                "role": team_member_role,
                "name": "",
                "faction": factions[player_side],
            }
            teams[player_side].append(team_member)

            square = chess_lib_square_to_square(chess_square)
            piece_role_by_square[square] = piece_role

        return teams, piece_role_by_square


class LichessCorrespondenceGamePresenterUrls(GamePresenterUrls):
    def htmx_game_no_selection_url(self, *, board_id: str) -> str:
        return "#"  # TODO

    def htmx_game_select_piece_url(self, *, square: "Square", board_id: str) -> str:
        return "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_select_piece",
                    kwargs={
                        "game_id": self._game_presenter.game_id,
                        "location": square,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_move_piece_url(self, *, square: "Square", board_id: str) -> str:
        assert self._game_presenter.selected_piece is not None  # type checker: happy
        return "".join(
            (
                reverse(
                    "lichess_bridge:htmx_game_move_piece",
                    kwargs={
                        "game_id": self._game_presenter.game_id,
                        "from_": self._game_presenter.selected_piece.square,
                        "to": square,
                    },
                ),
                "?",
                urlencode({"board_id": board_id}),
            )
        )

    def htmx_game_play_bot_move_url(self, *, board_id: str) -> str:
        return "#"  # TODO

    def htmx_game_play_solution_move_url(self, *, board_id: str) -> str:
        return "#"  # TODO

import io
from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple, Self, cast
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

    from .models import (
        LichessGameExport,
        LichessGameUser,
        LichessPlayerFullId,
        LichessPlayerId,
        LichessPlayerSide,
    )

# Presenters are the objects we pass to our templates.
_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING: dict["LichessPlayerSide", "PlayerSide"] = {
    "white": "w",
    "black": "b",
}


class _LichessGamePlayer(NamedTuple):
    id: "LichessPlayerId"
    username: "LichessPlayerFullId"
    player_side: "PlayerSide"


class _LichessGamePlayers(NamedTuple):
    me: _LichessGamePlayer
    them: _LichessGamePlayer

    @classmethod
    def from_game_data(
        cls, game_data: "LichessGameExport", my_player_id: "LichessPlayerId"
    ) -> Self:
        my_side: "LichessPlayerSide" = (
            "white" if game_data.players.white.user.id == my_player_id else "black"
        )
        their_side: "LichessPlayerSide" = "black" if my_side == "white" else "white"
        my_player: "LichessGameUser" = getattr(game_data.players, my_side).user
        their_player: "LichessGameUser" = getattr(game_data.players, their_side).user

        return cls(
            me=_LichessGamePlayer(
                id=my_player.id,
                username=my_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[my_side],
            ),
            them=_LichessGamePlayer(
                id=their_player.id,
                username=their_player.name,
                player_side=_LICHESS_PLAYER_SIDE_TO_PLAYER_SIDE_MAPPING[their_side],
            ),
        )


class LichessCorrespondenceGamePresenter(GamePresenter):
    def __init__(
        self,
        *,
        game_data: "LichessGameExport",
        my_player_id: "LichessPlayerId",
        refresh_last_move: bool,
        is_htmx_request: bool,
        selected_piece_square: "Square | None" = None,
    ):
        self._my_player_id = my_player_id
        self._game_data = game_data

        pgn_game = chess.pgn.read_game(io.StringIO(game_data.pgn))
        if not pgn_game:
            raise ValueError("Could not read PGN game")
        self._chess_board = pgn_game.end().board()
        fen = cast("FEN", self._chess_board.fen())

        teams, piece_role_by_square = self._create_teams_and_piece_role_by_square(
            self._chess_board, self.factions
        )

        # TODO: handle `last_move`
        super().__init__(
            fen=fen,
            piece_role_by_square=piece_role_by_square,
            teams=teams,
            refresh_last_move=refresh_last_move,
            is_htmx_request=is_htmx_request,
            selected_piece_square=selected_piece_square,
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
        return self._game_data.id

    @cached_property
    def factions(self) -> "Factions":
        return {
            self._players.me.player_side: "humans",
            self._players.them.player_side: "undeads",
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

    @cached_property
    def _players(self) -> _LichessGamePlayers:
        return _LichessGamePlayers.from_game_data(self._game_data, self._my_player_id)

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
        return "#"  # TODO

    def htmx_game_play_bot_move_url(self, *, board_id: str) -> str:
        return "#"  # TODO

    def htmx_game_play_solution_move_url(self, *, board_id: str) -> str:
        return "#"  # TODO

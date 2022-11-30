from ...models import Game
from ..types import ChessBoardState


def update_game_model(
    *,
    game: Game,
    board_state: ChessBoardState,
):
    game.fen = board_state.fen
    game.pieces_view = board_state.pieces_view
    game.active_player = board_state.active_player

    game.save(update_fields=["fen", "pieces_view", "active_player"])

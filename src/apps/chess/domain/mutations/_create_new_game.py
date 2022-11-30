from ...models import Game
from ..queries import get_chess_board_state


def create_new_game(*, is_versus_bot: bool, save: bool = True) -> Game:
    chess_board_state = get_chess_board_state()

    game = Game(
        fen=chess_board_state.fen,
        pieces_view=chess_board_state.pieces_view,
        is_versus_bot=is_versus_bot,
    )

    if save:
        game.save()

    return game

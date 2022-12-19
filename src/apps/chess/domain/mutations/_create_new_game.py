import chess

from ...models import Game, Team, TeamMember
from ..consts import PIECES_ROLE_BY_STARTING_SQUARE
from ..helpers import pieces_view_from_chess_board, square_from_int
from ..queries import generate_team_members
from ..types import PiecesIdPerSquare, PlayerSide

# Useful for quick tests:
_FEN_WHITE_ABOUT_TO_PROMOTE = "rn1qkbnr/p1P2ppp/b2p4/1p2p3/8/1P6/P1P1PPPP/RNBQKBNR w KQkq - 0 6"
_FEN_WHITE_ABOUT_TO_EN_PASSANT = "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
_FEN_BLACK_ABOUT_TO_MOVE_KING = "r1b1kb1r/ppp1qppp/2np1n2/3P4/8/2N1BN2/PPP2PPP/R2QKB1R w KQkq - 2 7"

_STARTING_BOARD = chess.Board()
_STARTING_PIECES_IDS_PER_SQUARE: PiecesIdPerSquare = {
    square_name: PIECES_ROLE_BY_STARTING_SQUARE[square_name]
    for square_name in [square_from_int(square) for square, piece in _STARTING_BOARD.piece_map().items()]
}
_STARTING_PIECES_VIEW = pieces_view_from_chess_board(_STARTING_BOARD, _STARTING_PIECES_IDS_PER_SQUARE)


def create_new_game(
    *, bot_side: PlayerSide | None, fen: str | None = None, pieces_ids_per_square: PiecesIdPerSquare | None = None
) -> Game:
    blank_one = fen is None
    chess_board = _STARTING_BOARD if blank_one else chess.Board(fen=fen)

    fen = chess_board.fen()
    active_player = "w" if chess_board.turn else "b"
    pieces_view = (
        _STARTING_PIECES_VIEW
        if blank_one or not pieces_ids_per_square
        else pieces_view_from_chess_board(chess_board, pieces_ids_per_square)
    )

    game = Game.objects.create(
        fen=fen,
        active_player=active_player,
        pieces_view=pieces_view,
        bot_side=bot_side,
    )

    for _ in range(2):
        # For the moment we'll just state that by convention the first Team is the "w" side,
        # while the second Team is the "b" side:
        team = Team.objects.create(game=game)
        team_members = []
        for team_member in generate_team_members():
            team_member.team = team
            team_members.append(team_member)
        TeamMember.objects.bulk_create(team_members)

    return game

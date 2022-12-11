from ...models import Game, Team, TeamMember
from ..queries import generate_team_members, get_chess_board_state
from ..types import PlayerSide


def create_new_game(*, bot_side: PlayerSide | None) -> Game:
    chess_board_state = get_chess_board_state()

    game = Game.objects.create(
        fen=chess_board_state.fen,
        pieces_view=chess_board_state.pieces_view,
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

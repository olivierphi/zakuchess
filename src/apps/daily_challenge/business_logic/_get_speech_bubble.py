import random
from typing import TYPE_CHECKING

from apps.chess.helpers import (
    player_side_to_chess_lib_color,
    square_from_int,
    team_member_role_from_piece_role,
)
from apps.chess.presenters import SpeechBubbleData

if TYPE_CHECKING:
    import chess

    from apps.chess.types import PlayerSide, Square, TeamMember
    from apps.daily_challenge.presenters import DailyChallengeGamePresenter

# This code was originally part of the DailyChallengeGamePresenter class,
# but as it grew arms and legs I ended up  moving it to its own file.


def get_speech_bubble(
    game_presenter: "DailyChallengeGamePresenter",
) -> SpeechBubbleData | None:
    if forced_speech_bubble := game_presenter.forced_speech_bubble:
        return SpeechBubbleData(
            text=forced_speech_bubble[1], square=forced_speech_bubble[0], time_out=2
        )

    if game_presenter.is_intro_turn:
        text = (
            game_presenter.challenge.intro_turn_speech_text
            or "Come on folks, we can win this one!"
        )
        return SpeechBubbleData(
            text=text,
            square=game_presenter.challenge.intro_turn_speech_square,
            time_out=8,
        )

    if game_presenter.is_bot_move and game_presenter.captured_piece_role:
        team_member_role = team_member_role_from_piece_role(
            game_presenter.captured_piece_role
        )
        captured_team_member: "TeamMember" = (
            game_presenter.team_members_by_role_by_side[
                game_presenter.challenge.my_side
            ][team_member_role]
        )
        if isinstance(name := captured_team_member["name"], str):
            # TODO: remove that code when we finished migrating to a list-name
            captured_team_member_display = name.split(" ")[0]
        else:
            captured_team_member_display = name[0]
        reaction = random.choice(
            ("They got {}!", "We lost {}!", "We'll avenge you, {}!")
        )
        return SpeechBubbleData(
            text=reaction.format(captured_team_member_display),
            square=_my_king_square(game_presenter),
            character_display=game_presenter.captured_piece_role,
        )

    if (
        game_presenter.is_bot_move
        and game_presenter.game_state["turns_counter"] > 1
        and game_presenter.game_state["current_attempt_turns_counter"] == 0
    ):
        return SpeechBubbleData(
            text="Let's try that again, folks! 🤞",
            square=game_presenter.challenge.intro_turn_speech_square,
        )

    if game_presenter.game_phase == "game_over:won":
        return SpeechBubbleData(
            text="We did it, folks! 🎉",
            square=_my_king_square(game_presenter),
        )

    if game_presenter.game_phase == "game_over:lost":
        return SpeechBubbleData(
            text="We win today, humans!",
            square=_bot_leftmost_piece_square(
                game_presenter.chess_board, game_presenter.challenge.bot_side
            ),
        )

    if game_presenter.selected_piece and game_presenter.selected_piece.is_pinned:
        return SpeechBubbleData(
            text="Moving would put our king in too much danger, I'm pinned here 😬",
            square=game_presenter.selected_piece.square,
        )

    if (
        game_presenter.is_player_turn
        and game_presenter.is_htmx_request
        and not game_presenter.restart_daily_challenge_ask_confirmation
        and not game_presenter.selected_piece
        and game_presenter.naive_score < -3
    ):
        probability = 0.6 if game_presenter.naive_score < -6 else 0.3
        die_result = random.random()  # 🎲
        if die_result > probability:
            return SpeechBubbleData(
                text="We're in a tough situation, folks 😬<br>"
                "Maybe restarting from the beginning, "
                "by using the ↩️ button below, could be a good idea?",
                square=_my_king_square(game_presenter),
                time_out=8,
            )

    return None


def _bot_leftmost_piece_square(
    chess_board: "chess.Board", bot_side: "PlayerSide"
) -> "Square":
    leftmost_rank = 9  # *will* be overridden by our loop
    leftmost_square: "Square" = "h8"  # ditto
    bot_color = player_side_to_chess_lib_color(bot_side)
    for square_int, piece in chess_board.piece_map().items():
        if piece.color != bot_color:
            continue
        square = square_from_int(square_int)
        rank = int(square[1])
        if rank < leftmost_rank:
            leftmost_rank = rank
            leftmost_square = square
    return leftmost_square


def _my_king_square(game_presenter: "DailyChallengeGamePresenter") -> "Square":
    return _king_square(game_presenter.chess_board, game_presenter.challenge.my_side)


def _king_square(chess_board: "chess.Board", player_side: "PlayerSide") -> "Square":
    return square_from_int(
        chess_board.king(player_side_to_chess_lib_color(player_side))
    )

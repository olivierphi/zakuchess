from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from apps.chess.types import Factions, PlayerSide

# If the solution can be found in 8 turns for example, we'll give 40 turns to the player
MAXIMUM_TURNS_PER_CHALLENGE_SOLUTION_MULTIPLIER: Final[int] = 5

PLAYER_SIDE: "Final[PlayerSide]" = "w"
BOT_SIDE: "Final[PlayerSide]" = "b"
FACTIONS: "Final[Factions]" = {"w": "humans", "b": "undeads"}  # hard-coded for now

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from apps.chess.types import Factions, PlayerSide

MAXIMUM_TURNS_PER_CHALLENGE: Final[int] = 40

PLAYER_SIDE: "Final[PlayerSide]" = "w"
BOT_SIDE: "Final[PlayerSide]" = "b"
FACTIONS: "Final[Factions]" = {"w": "humans", "b": "undeads"}  # hard-coded for now

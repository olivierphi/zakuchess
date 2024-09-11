from typing import TYPE_CHECKING, Final

from apps.chess.models import GameFactions

if TYPE_CHECKING:
    from apps.chess.types import PlayerSide

PLAYER_SIDE: "Final[PlayerSide]" = "w"
BOT_SIDE: "Final[PlayerSide]" = "b"
FACTIONS: "Final[GameFactions]" = GameFactions(
    w="humans", b="undeads"
)  # hard-coded for now

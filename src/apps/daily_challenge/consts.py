from __future__ import annotations

from typing import TYPE_CHECKING, Final

from apps.chess.types import GameFactions

if TYPE_CHECKING:
    from apps.chess.types import PlayerSide

PLAYER_SIDE: Final[PlayerSide] = "w"

BOT_SIDE: Final[PlayerSide] = "b"

FACTIONS: Final[GameFactions] = GameFactions(
    # hard-coded for now, but hopefully we'll make this less binary later on
    w="humans",
    b="undead",
)

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .types import File, Rank

FILES: Final[tuple[File, ...]] = ("a", "b", "c", "d", "e", "f", "g", "h")
RANKS: Final[tuple[Rank, ...]] = ("1", "2", "3", "4", "5", "6", "7", "8")

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from .types import Character, GameTeamsDict, PlayerSide


class GameTeams(NamedTuple):
    """
    We'll use this immutable class to store the characters for each player side.
    """

    w: tuple[Character, ...]  # "w" player's characters
    b: tuple[Character, ...]  # "b" player's characters

    def get_team_for_side(self, item: PlayerSide) -> tuple[Character, ...]:
        return getattr(self, item)

    def to_dict(self) -> GameTeamsDict:
        """
        Used to store that in the database
        """
        return {"w": list(self.w), "b": list(self.b)}

    @classmethod
    def from_dict(cls, data: GameTeamsDict) -> GameTeams:
        """
        Used to re-hydrate the data from the database.
        """
        return cls(
            w=tuple(Character(*char) for char in data["w"]),  # type: ignore[misc]
            b=tuple(Character(*char) for char in data["b"]),  # type: ignore[misc]
        )

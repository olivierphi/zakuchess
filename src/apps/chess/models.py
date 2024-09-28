import enum
from typing import TYPE_CHECKING, NamedTuple, Self

import msgspec
from django.db import models

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .types import Faction, GameTeamsDict, PlayerSide, TeamMemberRole


# MsgSpec doesn't seem to be handling Django Choices correctly, so we have one
# "Python enum" for the Struct and one `models.IntegerChoices` derived from it for
# Django-related operations (such a forms)  😔


class UserPrefsGameSpeed(enum.IntEnum):
    NORMAL = 1
    FAST = 2


class UserPrefsGameSpeedChoices(models.IntegerChoices):
    NORMAL = UserPrefsGameSpeed.NORMAL, "Normal"
    FAST = UserPrefsGameSpeed.FAST, "Fast"


class UserPrefsBoardTexture(enum.IntEnum):
    NO_TEXTURE = 0
    ABSTRACT = 1


class UserPrefsBoardTextureChoices(models.IntegerChoices):
    NO_TEXTURE = (
        UserPrefsBoardTexture.NO_TEXTURE,
        "No texture: the chess squares are only made of 2 colours",
    )
    ABSTRACT = (
        UserPrefsBoardTexture.ABSTRACT,
        "Abstract texture: an abstract texture is applied to the chess board",
    )


class UserPrefs(
    msgspec.Struct,
    kw_only=True,  # type: ignore[call-arg]
    rename={
        # ditto
        "game_speed": "gs",
        "board_texture": "bt",
    },
):
    """
    This is the player's preferences, stored within their own cookie.
    Contrary to the PlayerSessionContent, this cookie is not signed as there is really
    no need to: if players hack with this cookie's content it won't be a big deal :-)
    """

    game_speed: UserPrefsGameSpeed = UserPrefsGameSpeed.NORMAL
    board_texture: UserPrefsBoardTexture = UserPrefsBoardTexture.ABSTRACT

    def to_cookie_content(self) -> str:
        return msgspec.json.encode(self).decode()

    @classmethod
    def from_cookie_content(cls, cookie_content: str) -> Self:
        return msgspec.json.decode(cookie_content.encode(), type=cls)


class GameFactions(NamedTuple):
    w: "Faction"  # the faction for the "w" player
    b: "Faction"  # the faction for the "b" player

    def get_faction_for_side(self, item: "PlayerSide") -> "Faction":
        return getattr(self, item)


class TeamMember(NamedTuple):
    role: "TeamMemberRole"
    name: "Sequence[str]"
    faction: "Faction | None" = None


class GameTeams(NamedTuple):
    """
    We'll use this immutable class to store the team members for each player side.
    """

    w: tuple["TeamMember", ...]  # the team members for the "w" player
    b: tuple["TeamMember", ...]  # the team members for the "b" player

    def get_team_for_side(self, item: "PlayerSide") -> "tuple[TeamMember]":
        return getattr(self, item)

    def to_dict(self) -> "GameTeamsDict":
        """
        Used to store that in the database
        """
        return {"w": list(self.w), "b": list(self.b)}

    @classmethod
    def from_dict(cls, data: "GameTeamsDict") -> "GameTeams":
        """
        Used to re-hydrate the data from the database.
        """
        return cls(
            w=tuple(TeamMember(*member) for member in data["w"]),
            b=tuple(TeamMember(*member) for member in data["b"]),
        )

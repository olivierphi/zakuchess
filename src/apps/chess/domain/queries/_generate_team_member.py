from random import choice
from typing import TYPE_CHECKING

from ...models import TeamMember

if TYPE_CHECKING:
    from ..types import TeamMemberRole


def generate_team_member(*, role: "TeamMemberRole") -> TeamMember:
    return TeamMember(
        first_name=choice(_FIRST_NAMES),
        last_name=choice(_LAST_NAMES),
        role=role,
    )


_FIRST_NAMES = (
    "Nico",
    "Oliv",
    "Elise",
    "Quentin",
    "Syd",
    "Jo",
    "Rae",
    "Ngee",
    "Ludo",
    "Stephen",
    "Laurie",
    "Luca",
    "Justine",
    "Benjamin",
    "Lea",
    "Leo",
    "Leon",
    "Inigo",
    "Pat",
    "John",
    "Seppo",
    "Emma",
    "Chris",
    "Louise",
    "Lorna",
    "Aruki",
    "Motoko",
    "Takeshi",
    "Tetsuo",
    "Kaneda",
    "Ryu",
    "Terry",
    "Kelly",
    "Vijay",
    "Ken",
    "Ali",
    "Babakar",
    "Mohamed",
    "Souleymane",
    "Mamadou",
    "Luis",
    "Jose",
    "Ti",
    "Lam",
    "Linh",
    "Simon",
    "Jean-Michel",
)

_LAST_NAMES = (
    "Philippon",
    "Warren",
    "Goussin",
    "Vignon",
    "André",
    "Leboswky",
    "Kitano",
    "Montoya",
    "Murakami",
    "Kusanagi",
    "Gohan",
    "Peralta",
    "Holt",
    "Santiago",
    "Jeffords",
    "Schrute",
    "Scott",
    "Devi",
    "Kapoor",
    "Khan",
    "Kowalski",
    "Müller",
    "Hansen",
    "Kim",
    "Wang",
    "Wong",
    "Nguyen",
    "Cissé",
    "Diop",
    "González",
    "Rodríguez",
    "Martinez",
    "García",
    "Silva",
    "Hernandez",
    "Lopez",
    "Gomez",
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

    from apps.authentication.models import User


def user_is_staff(user: "User | AnonymousUser") -> bool:
    return user.is_staff

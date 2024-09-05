from typing import TYPE_CHECKING

import berserk

if TYPE_CHECKING:
    from .models import LichessAccessToken


def get_lichess_api_client(access_token: "LichessAccessToken") -> berserk.Client:
    return _create_lichess_api_client(access_token)


# This is the function we'll mock during tests:
def _create_lichess_api_client(access_token: "LichessAccessToken") -> berserk.Client:
    session = berserk.TokenSession(access_token)
    return berserk.Client(session=session)

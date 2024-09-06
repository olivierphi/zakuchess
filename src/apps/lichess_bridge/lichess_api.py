from typing import TYPE_CHECKING

import berserk
from asgiref.sync import sync_to_async

from .models import LICHESS_ACCESS_TOKEN_PREFIX

if TYPE_CHECKING:
    from .models import LichessAccessToken


def is_lichess_api_access_token_valid(token: str) -> bool:
    return token.startswith(LICHESS_ACCESS_TOKEN_PREFIX) and len(token) > 10


@sync_to_async(thread_sensitive=False)
def get_lichess_my_account(
    access_token: "LichessAccessToken",
) -> berserk.types.AccountInformation:
    return _get_lichess_api_client(access_token).account.get()


def _get_lichess_api_client(access_token: "LichessAccessToken") -> berserk.Client:
    return _create_lichess_api_client(access_token)


# This is the function we'll mock during tests:
def _create_lichess_api_client(access_token: "LichessAccessToken") -> berserk.Client:
    session = berserk.TokenSession(access_token)
    return berserk.Client(session=session)

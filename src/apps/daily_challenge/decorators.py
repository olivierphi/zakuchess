import functools

from django.core.exceptions import BadRequest

from apps.chess.types import ChessLogicException


def handle_chess_logic_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChessLogicException as exc:
            raise BadRequest(str(exc)) from exc

    return wrapper

from __future__ import annotations


class ChessLogicException(Exception):
    pass


class ChessInvalidStateException(ChessLogicException):
    pass


class ChessInvalidActionException(ChessLogicException):
    pass


class ChessInvalidMoveException(ChessInvalidActionException):
    pass

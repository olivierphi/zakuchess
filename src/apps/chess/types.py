from typing import Literal, Required, TypeAlias, TypedDict

FEN: TypeAlias = str

PlayerSide = Literal[
    # Following chess conventions, our sides will be "w(hite)" and "b(lack)".
    # fmt: off
    "w",
    "b",
    # fmt: on
]


PieceType = Literal[
    # fmt: off
    "p", "n", "b", "r", "q", "k",
    # fmt: on
]

PieceSymbol = Literal[
    # fmt: off
    # "w" side:
    "P", "N", "B", "R", "Q", "K",
    # "b" side:
    "p", "n", "b", "r", "q", "k",
    # fmt: on
]

PieceName = Literal["pawn", "knight", "bishop", "rook", "queen", "king"]


TeamMemberRole = Literal[
    # fmt: off
    # 8 pawns:
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8",
    # 8 pieces:
    "r1", "n1", "b1", "q", "k", "b2", "n2", "r2",
    # fmt: on
]

PieceRole = Literal[
    # fmt: off
    # Same than TeamMemberRole, but applied to the board:
    # --> following chess conventions, "w player"'s pieces are uppercase while "b player"'s pieces are lowercase.
    # ----- "w" player side:
    "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8",
    "R1", "N1", "B1", "Q", "K", "B2", "N2", "R2",
    # Promoted pawns have a 3 letters role, where the last one is the promoted piece:
    # Let's consider "Queen" promotions only for now:
    "P1Q", "P2Q", "P3Q", "P4Q", "P5Q", "P6Q", "P7Q", "P8Q",
    # ----- "b" player side:
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8",
    "r1", "n1", "b1", "q", "k", "b2", "n2", "r2",
    # And same for "b" side promotions:
    "p1q", "p2q", "p3q", "p4q", "p5q", "p6q", "p7q", "p8q",
    # fmt: on
]

File = Literal["a", "b", "c", "d", "e", "f", "g", "h"]
Rank = Literal["1", "2", "3", "4", "5", "6", "7", "8"]

Square = Literal[
    # fmt: off
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
    # fmt: on
]

MoveTuple = tuple[Square, Square]

SquareColor = Literal["light", "dark"]


PieceRoleBySquare: TypeAlias = dict[Square, PieceRole]


GamePhase = Literal[
    "waiting_for_player_selection",
    "waiting_for_player_target_choice",
    "opponent_piece_selected",
    "waiting_for_player_target_choice_confirmation",
    "waiting_for_bot_turn",
    "waiting_for_opponent_turn",
    "game_over:won",
    "game_over:lost",
]

GameEndReason = Literal[
    "checkmate",
    "stalemate",
    "insufficient_material",
    "seventyfive_moves",
    "threefold_repetition",
    "fivefold_repetition",
    "fivefold_repetition",
    "fifty_moves",
]


Faction = Literal[
    "humans",
    "undeads",
]

Factions: TypeAlias = dict[PlayerSide, Faction]


class GameOverDescription(TypedDict):
    winner: "PlayerSide | None"
    reason: "GameEndReason"


class ChessMoveResult(TypedDict):
    fen: "FEN"
    moves: list[MoveTuple]
    is_capture: bool
    captured: Square | None
    is_castling: bool
    promotion: "PieceType | None"
    game_over: GameOverDescription | None


class TeamMember(TypedDict, total=False):
    role: Required["TeamMemberRole"]
    # TODO: change this to just `lst[str]` when we finished migrating to a list-name
    name: Required[list[str] | str]
    faction: "Faction"


GameTeams: TypeAlias = dict["PlayerSide", list["TeamMember"]]


class ChessLogicException(Exception):
    pass


class ChessInvalidStateException(ChessLogicException):
    pass


class ChessInvalidActionException(ChessLogicException):
    pass


class ChessInvalidMoveException(ChessInvalidActionException):
    pass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Square


class ChessSquareConverter:
    regex = "[a-h][1-8]"

    def to_python(self, value: str) -> "Square":
        return value  # type: ignore

    def to_url(self, value: "Square") -> str:
        return value  # type: ignore

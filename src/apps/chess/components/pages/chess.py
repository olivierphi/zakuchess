from typing import TYPE_CHECKING


from .. import chess
from apps.webui.components.layout import document

if TYPE_CHECKING:
    from django.http import HttpRequest
    from dominate.tags import dom_tag
    from ...presenters import GamePresenter


def chess_page(*, game_presenter: "GamePresenter", request: "HttpRequest") -> "dom_tag":
    return document(
        children=[
            chess.chess_arena(game_presenter=game_presenter),
        ],
        request=request,
    )

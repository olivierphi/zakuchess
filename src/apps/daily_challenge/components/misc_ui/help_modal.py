from typing import TYPE_CHECKING

from dominate.tags import div, h3

from apps.chess.components.misc_ui import modal_container

from .help import help_content
from .svg_icons import ICON_SVG_HELP

if TYPE_CHECKING:
    from dominate.tags import dom_tag

    from ...presenters import DailyChallengeGamePresenter

# TODO: manage i18n


def help_modal(*, game_presenter: "DailyChallengeGamePresenter") -> "dom_tag":
    return modal_container(
        header=h3(
            "How to play ",
            ICON_SVG_HELP,
            cls="text-xl",
        ),
        body=div(
            help_content(
                challenge_total_turns=game_presenter.challenge_total_turns,
                factions_tuple=tuple(game_presenter.factions.items()),
            ),
            cls="p-6 space-y-6",
        ),
    )

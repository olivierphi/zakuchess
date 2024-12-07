from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dominate.tags import div

from apps.chess.components.chess_board import INFO_BARS_COMMON_CLASSES
from apps.chess.components.svg_icons import ICON_SVG_CANCEL, ICON_SVG_CONFIRM
from apps.webui.components.atoms.buttons import zc_button

if TYPE_CHECKING:
    from collections.abc import Mapping

    from dominate.dom_tag import dom_tag

CompanionBarPosition = Literal["top", "bottom"]


def companion_bar(
    inner_content: dom_tag,
    *,
    position: CompanionBarPosition,
    extra_attrs: Mapping[str, str | bool] | None = None,
    htmx_attrs: Mapping[str, str | bool] | None = None,
    id_: str | None = None,
) -> dom_tag:
    attributes = {
        **(extra_attrs or {}),
        **(htmx_attrs or {}),
    }
    if id_:
        attributes["id"] = id_

    classes = (
        f"min-h-[4rem] flex items-center justify-center {INFO_BARS_COMMON_CLASSES}"
    )
    match position:
        case "top":
            classes += " border-t-0 xl:border-2 xl:rounded-t-md"
        case "bottom":
            classes += " border-t-0 rounded-b-md"

    return div(
        inner_content,
        cls=classes,
        **attributes,
    )


def confirmation_dialog_bar(
    *,
    question: dom_tag,
    htmx_attrs_confirm: Mapping[str, str | bool],
    htmx_attrs_cancel: Mapping[str, str | bool],
    id_: str | None = None,
) -> dom_tag:
    inner_content = div(
        question,
        div(
            zc_button(
                "Confirm",
                button_type="confirm",
                svg_icon=ICON_SVG_CONFIRM,
                htmx_attrs=htmx_attrs_confirm,
            ),
            zc_button(
                "Cancel",
                svg_icon=ICON_SVG_CANCEL,
                button_type="cancel",
                htmx_attrs=htmx_attrs_cancel,
            ),
            cls="text-center",
        ),
    )

    return companion_bar(inner_content=inner_content, position="top", id_=id_)

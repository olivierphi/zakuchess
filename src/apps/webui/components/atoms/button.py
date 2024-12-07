from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from dominate.dom_tag import dom_tag
from dominate.tags import a, button, span

if TYPE_CHECKING:
    from collections.abc import Sequence

    from dominate.tags import dom_tag

ButtonType = Literal["action", "confirm", "cancel"]

_BUTTON_BASE_BG_COLOR, _BUTTON_BASE_TEXT_COLOR = "bg-rose-600", "text-slate-200"
_BUTTON_BASE_HOVER_TEXT_COLOR = "hover:text-stone-100"
_BUTTON_CLASSES = (
    "inline-block py-1 px-3 rounded-md font-bold whitespace-nowrap "
    f"{_BUTTON_BASE_TEXT_COLOR} {_BUTTON_BASE_BG_COLOR} {_BUTTON_BASE_HOVER_TEXT_COLOR}"
)
_BUTTON_CONFIRM_CLASSES = _BUTTON_CLASSES.replace(_BUTTON_BASE_BG_COLOR, "bg-lime-700")
_BUTTON_CANCEL_CLASSES = _BUTTON_CLASSES.replace(_BUTTON_BASE_BG_COLOR, "bg-indigo-500")

_BUTTON_TYPE_TO_CLASS_MAPPING: dict[ButtonType, str] = {
    "action": _BUTTON_CLASSES,
    "confirm": _BUTTON_CONFIRM_CLASSES,
    "cancel": _BUTTON_CANCEL_CLASSES,
}


def zc_button(
    label: str,
    *,
    button_type: ButtonType,
    svg_icon: str | None = None,
    href: str | None = None,  # if href is not None, the button will be an HTML anchor
    id_: str | None = None,
    title: str | None = None,
    html_type: str | None = None,
    additional_classes: Sequence[str] | None = None,
    additional_attributes: dict | None = None,
    htmx_attributes: dict | None = None,
    is_a_help_for_actual_button: bool = False,
) -> dom_tag:
    """A 'zakuchess' (`zc_*`) button."""

    if is_a_help_for_actual_button and htmx_attributes is not None:
        raise ValueError(
            "Elements that are not actual buttons but "
            "an help for them should not have htmx attributes"
        )

    children: list[str] = [label]
    if svg_icon:
        children.extend((" ", svg_icon))

    classes: list[str] = [_BUTTON_TYPE_TO_CLASS_MAPPING[button_type]]
    if additional_classes:
        classes.extend(additional_classes)

    attributes: dict = {
        **(additional_attributes or {}),
        **(htmx_attributes or {}),
    }
    if id_:
        attributes["id"] = id_
    if title:
        attributes["title"] = title
    if html_type:
        attributes["type"] = html_type

    if is_a_help_for_actual_button:
        classes.extend(("!inline-block", "!mx-0"))
        return span(
            *children,
            cls=" ".join(classes),
            **attributes,
        )

    if href:
        return a(
            *children,
            href=href,
            cls=" ".join(classes),
            **attributes,
        )

    return button(
        *children,
        cls=" ".join(classes),
        **attributes,
    )


def zc_header_icon_button(
    *, icon: str, title: str, id_: str, htmx_attributes: dict[str, str]
) -> dom_tag:
    return button(
        icon,
        cls="block px-1 py-1 text-sm text-slate-50 hover:text-slate-400",
        title=title,
        id=id_,
        **htmx_attributes,
    )

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal, TypeAlias

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

register = template.Library()

_logger = logging.getLogger(__name__)

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

SvgDefinition: TypeAlias = SafeString
_SVG_ICONS_REGISTRY: dict[str, SvgDefinition] = {}


def register_svg_icons(icons: dict[str, SvgDefinition]) -> None:
    _SVG_ICONS_REGISTRY.update(icons)
    _logger.debug("Registered SVG icons: %s", ", ".join(icons.keys()))


@register.simple_tag
def zc_button(
    label: str,
    *,
    button_type: ButtonType,
    icon: str | None = None,
    href: str | None = None,  # if href is not None, the button will be a <a href="...">
    id_: str | None = None,
    title: str | None = None,
    html_type: str | None = None,
    extra_classes: Sequence[str] | None = None,
    extra_attrs: Mapping[str, str | bool] | None = None,
    htmx_attrs: Mapping[str, str | bool] | None = None,
    is_a_help_for_actual_button: bool = False,  # if True, the button will be a <span>
) -> SafeString:
    """A 'zakuchess' (`zc_*`) button."""

    if is_a_help_for_actual_button and htmx_attrs is not None:
        raise ValueError(
            "Elements that are not actual buttons but "
            "an help for them should not have htmx attributes"
        )

    children: list[str] = [label]
    if icon:
        try:
            children.extend((" ", _SVG_ICONS_REGISTRY[icon]))
        except KeyError:
            raise ValueError(
                f"Unknown icon: {icon} (available: {tuple(_SVG_ICONS_REGISTRY.keys())}"
            )

    classes: list[str] = [_BUTTON_TYPE_TO_CLASS_MAPPING[button_type]]
    if extra_classes:
        classes.extend(extra_classes)

    attributes: dict = {
        **(extra_attrs or {}),
        **(htmx_attrs or {}),
    }
    if id_:
        attributes["id"] = id_
    if title:
        attributes["title"] = title
    if html_type:
        attributes["type"] = html_type

    if is_a_help_for_actual_button:
        classes.extend(("!inline-block", "!mx-0"))
        node = "span"
    elif href:
        node = "a"
        attributes["href"] = href
    else:
        node = "button"

    return format_html(
        '<{node} class="{classes}" {attributes}>{children}</{node}>',
        node=node,
        classes=" ".join(classes),
        attributes=format_html_join(" ", '{}="{}"', attributes.items()),
        children=format_html_join("", "{}", ((child,) for child in children)),
    )

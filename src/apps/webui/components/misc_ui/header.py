from typing import TYPE_CHECKING

from dominate.tags import button

if TYPE_CHECKING:
    from dominate.tags import dom_tag


def header_button(
    *, icon: str, title: str, id_: str, htmx_attributes: dict[str, str]
) -> "dom_tag":
    return button(
        icon,
        cls="block px-1 py-1 text-sm text-slate-50 hover:text-slate-400",
        title=title,
        id=id_,
        **htmx_attributes,
    )

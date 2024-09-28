from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    import enum
    from collections.abc import Sequence

DjangoChoice: TypeAlias = tuple[str | int | float, str]


def enum_to_django_choices(enum_class: "type[enum.Enum]") -> "Sequence[DjangoChoice]":
    return [(enum_member.name, enum_member.value) for enum_member in enum_class]


def literal_to_django_choices(literal: "type[Literal]") -> "Sequence[DjangoChoice]":  # type: ignore[valid-type]
    return [(value, value) for value in literal.__args__]

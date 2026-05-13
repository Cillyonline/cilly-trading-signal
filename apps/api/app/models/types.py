from enum import StrEnum

from sqlalchemy import Enum


def enum_values(enum_class: type[StrEnum]) -> Enum:
    return Enum(enum_class, values_callable=lambda values: [item.value for item in values])

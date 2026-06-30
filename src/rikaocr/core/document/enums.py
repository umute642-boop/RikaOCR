# SPDX-License-Identifier: Apache-2.0
"""Enumerations used by the document model.

String-valued enums are used so that values serialise to readable, stable
strings (important for the PAGE/JSONL round-trip introduced in M2).
"""

from __future__ import annotations

from enum import StrEnum


class RegionType(StrEnum):
    """The kind of layout region on a page."""

    PARAGRAPH = "paragraph"
    MARGINALIA = "marginalia"
    HEADER = "header"
    SEAL = "seal"
    TABLE = "table"
    OTHER = "other"


class ReadingDirection(StrEnum):
    """Text reading direction. Rik'a (Arabic script) is right-to-left."""

    RTL = "rtl"
    LTR = "ltr"


__all__ = ["RegionType", "ReadingDirection"]

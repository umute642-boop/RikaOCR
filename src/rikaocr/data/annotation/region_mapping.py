# SPDX-License-Identifier: Apache-2.0
"""Mapping between PAGE-XML ``TextRegion@type`` values and :class:`RegionType`.

PAGE defines a richer set of region types than the document model needs; unknown
or unmapped values fall back to ``RegionType.OTHER``. The mapping is chosen so
that ``region_type_from_page(region_type_to_page(x)) == x`` for every
``RegionType`` (a stable round-trip).
"""

from __future__ import annotations

from rikaocr.core.document.enums import RegionType

PAGE_TO_REGION: dict[str, RegionType] = {
    "paragraph": RegionType.PARAGRAPH,
    "heading": RegionType.HEADER,
    "header": RegionType.HEADER,
    "marginalia": RegionType.MARGINALIA,
    "table": RegionType.TABLE,
    "stamp": RegionType.SEAL,
    "seal": RegionType.SEAL,
}

REGION_TO_PAGE: dict[RegionType, str] = {
    RegionType.PARAGRAPH: "paragraph",
    RegionType.HEADER: "heading",
    RegionType.MARGINALIA: "marginalia",
    RegionType.TABLE: "table",
    RegionType.SEAL: "stamp",
    RegionType.OTHER: "other",
}


def region_type_from_page(value: str | None) -> RegionType:
    """Map a PAGE ``TextRegion@type`` value to a :class:`RegionType`."""
    if value is None:
        return RegionType.OTHER
    return PAGE_TO_REGION.get(value.lower(), RegionType.OTHER)


def region_type_to_page(region_type: RegionType) -> str:
    """Map a :class:`RegionType` to a PAGE ``TextRegion@type`` value."""
    return REGION_TO_PAGE.get(region_type, "other")


__all__ = [
    "PAGE_TO_REGION",
    "REGION_TO_PAGE",
    "region_type_from_page",
    "region_type_to_page",
]
